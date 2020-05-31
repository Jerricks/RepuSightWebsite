from app import app
from flask import session
import datetime
from .model_summary import check_collection
from .model_email import send_mail
import json
from bson import json_util

tech_recepients = ["niki.upadhyay@repusight.com"]


def sourcesList():
    collection = check_collection()
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    data = []
    final_data = []
    if city_all == "True":
        al = list(collection.aggregate(
            [{ "$match":  {"Name": name, "City": city}},{"$group": {"_id": {"Name": name, "City": city, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"]})
    else:
        al = list(collection.aggregate(
            [{ "$match":  {"Name": name, "Place": place}},{"$group": {"_id": {"Name": name, "Place": place, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"]})
    final_data = sorted(data, key=lambda x: x['Channel'])
    return final_data


def socialmediaList():
    data = []
    data.append({"Channel": "Facebook", "icon": "/static/images/fb.png"})
    data.append({"Channel": "Instagram", "icon": "/static/images/instagram.png"})
    data.append({"Channel": "Twitter", "icon": "/static/images/twitter.png"})
    final_data = sorted(data, key=lambda x: x['Channel'])
    return final_data


def replyCredDetails():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if city_all == "True":
        place = city
    al = app.config['REPLYCREDENTIALS_COLLECTION'].find({"Name": name, "Place": place, "City": city})
    return json.loads(json_util.dumps(al))


def saveData(user_id,password,channel):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if city_all == "True":
        place = city
    try:
        al = list(app.config['REPLYCREDENTIALS_COLLECTION'].find({"Name": name, "Place": place, "City": city, "Channel": channel}))
        app.config['REPLYCREDENTIALS_COLLECTION'].update({"Channel": channel, "Name": name, "Place": place, "City": city},
            {"UserId": user_id, "Password": password, "Channel": channel, "Name": name, "Place": place, "City": city, "ChannelUrl": al[0]['ChannelUrl']}, upsert=True)
        print("Credentials Saved")
        recipients = tech_recepients
        esubject = "Reply Credential Details updated on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for " + name + ", " + place + ", " + city + "(" + channel + ")"
        ebody = "Details are, \nUser Id: " + user_id + "\nPassword: " + password
        ebody = ebody + "\n\nRepusight Support."
        #send_mail(recipients, esubject, ebody)
        status = "Success"
        return status
    except Exception as e:
        print("Credentials are not saved")
        recipients = tech_recepients
        esubject = "Error while updating credentials on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p")
        ebody = "For " + name + ", " + place + ", " + city + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\n\nRepusight Support."
        #send_mail(recipients, esubject, ebody)
        status = "Error"
        return status


def saveDataSM(keyword, smsource):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    username = user_obj['_id']
    try:
        if smsource == 'Facebook':
            app.config['SOCIALMEDIADATA_COLLECTION'].update({"_id": username, "hotel": name, "Place": place},
                {"$set":{"_id": username, "hotel": name, "Place": place, "fbkeyword": keyword}}, upsert=True)
        if smsource == 'Instagram':
            app.config['SOCIALMEDIADATA_COLLECTION'].update({"_id": username, "hotel": name, "Place": place},
                {"$set":{"_id": username, "hotel": name, "Place": place, "instagramkeyword": keyword}}, upsert=True)
        if smsource == 'Twitter':
            app.config['SOCIALMEDIADATA_COLLECTION'].update({"_id": username, "hotel": name, "Place": place},
                {"$set":{"_id": username, "hotel": name, "Place": place, "twitterkeyword": keyword}}, upsert=True)
        print("Credentials Saved")
        status = "Success"
        return status
    except Exception as e:
        print("Credentials are not saved")
        status = "Error"
        return status


def smKeyword():
    user_obj = session.get('user', None)
    username = user_obj['_id']
    al = app.config['SOCIALMEDIADATA_COLLECTION'].find({"_id": username})
    return json.loads(json_util.dumps(al))