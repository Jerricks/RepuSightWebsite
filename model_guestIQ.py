from app import app
from flask import session
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests, json
from datetime import datetime
import pandas as pd

ip = '127.0.0.1'
port = 27017
DB_NAME = 'scotchbox'
DATABASE = MongoClient(ip, port)[DB_NAME]


def guestData():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    data = []
    customerData = list(DATABASE.customers.find({"name": name}))
    if customerData:
        customer_id = customerData[0]['_id']
        con = list(DATABASE.connections.find({"customer_id": str(customer_id), "status": 1}))
        if con:
            deviceId = []
            for connections in con:
                deviceId.append(connections["device_id"])
            for device in deviceId:
                deviceData = list(DATABASE.devices.find({"_id": ObjectId(device)}))
                if deviceData:
                    phoneNo = deviceData[0]["phone"]
                    socialData = list(DATABASE.social_accounts.find({"device_id": device}))
                    if socialData:
                        userName = socialData[0]["name"]
                        userPic = "http://graph.facebook.com/" + socialData[0][
                            "provider_user_id"] + "/picture?type=large"
                        userEmail = socialData[0]["email"]
                        userGender = socialData[0]["gender"]
                        userHometown = "Unknown"
                    else:
                        userName = "Anonymous"
                        userPic = "/static/images/anonymous-user.jpeg"
                        userEmail = "Unknown"
                        userGender = "Unknown"
                        userHometown = "Unknown"
                    if user_obj['propType'] == 'Hotel':
                        surveyData = list(DATABASE.hotel_surveys.find({"device_id": device}))
                    else:
                        surveyData = list(DATABASE.restaurant_surveys.find({"device_id": device}))
                    sug_data = []
                    if surveyData:
                        for survey in surveyData:
                            suggestions = survey["suggestion"]
                            sug_date = survey["created_at"]
                            sug_data.append({"suggestions": suggestions, "sug_date": sug_date})
                    else:
                        sug_data.append({"suggestions": "No notes availabe", "sug_date": ""})
                    historyData = list(DATABASE.connections.find({"device_id": device, "status": 2}))
                    his_data = []
                    df = pd.DataFrame(columns=["last_visit", "property", "placeType"])
                    for past in historyData:
                        pastDate = past["created_at"]
                        d = datetime.strptime(str(pastDate), '%Y-%m-%d %H:%M:%S.%f')
                        last_visit = d.strftime('%Y-%m-%d')
                        ind = next(index for (index, d) in enumerate(customerData) if d["_id"] == customer_id)
                        property = customerData[ind]["name"]
                        customer_category_id = customerData[0]["customer_category_id"]
                        customer_category_data = list(
                            DATABASE.customer_categories.find({"_id": ObjectId(customer_category_id)}))
                        placeType = customer_category_data[0]["name"]
                        his_data.append({"last_visit": last_visit, "property": property, "placeType": placeType})
                    for i in range(len(his_data)):
                        df.loc[i] = [his_data[i]["last_visit"], his_data[i]["property"], his_data[i]["placeType"]]
                    series1 = df.groupby(['property']).size()
                    df2 = pd.DataFrame({"property": series1.index, "Count": series1.values})
                    series2 = df.groupby(['property'])["last_visit"].max()
                    df3 = pd.DataFrame({"property": series2.index, "last_visit": series2.values})
                    df4 = pd.merge(df2, df3, on="property")
                    df4 = pd.merge(df4, df[['property', 'placeType']], on='property', how="left")
                    df4 = df4.drop_duplicates()
                    data.append({"phoneNo": phoneNo, "userName": userName, "userPic": userPic, "userEmail": userEmail,
                                 "userGender": userGender, "userHometown": userHometown, "notesData": sug_data,
                                 "historyData": df4})
        else:
            data.append({"phoneNo": "None", "userName": "None", "userPic": "/static/images/anonymous-user.jpeg",
                         "userEmail": "None",
                         "userGender": "None", "userHometown": "None", "notesData": "", "historyData": pd.DataFrame()})
    else:
        data.append({"phoneNo": "None", "userName": "None", "userPic": "/static/images/anonymous-user.jpeg",
                     "userEmail": "None",
                     "userGender": "None", "userHometown": "None", "notesData": "", "historyData": pd.DataFrame()})
    return data
