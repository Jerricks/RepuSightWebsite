from app import app
from flask import session
import datetime
from .model_email import send_mail
import json
from bson import json_util

tech_recepients = ["niki.upadhyay@repusight.com"]

topicHotel = ['Food', 'Service', 'Value', 'Ambience', 'Cleanliness', 'Amenities', 'Hospitality', 'Location',
              'Front-Desk', 'Room']

topicRestaurant = ['Taste', 'Variety', 'Drinks', 'Service', 'Value', 'Hygiene', 'Ambience', 'Hospitality', 'Comforts',
                   'Entertainment']


def get_collection():
    user_obj = session.get('user', None)
    if user_obj['propType'] == 'Hotel':
        connect = app.config['DEPTHOTEL_COLLECTION']
    elif user_obj['propType'] == 'Restaurant':
        connect = app.config['DEPTRESTAURANT_COLLECTION']
    return connect


def check_proptype():
    user_obj = session.get('user', None)
    if user_obj['propType'] == 'Hotel':
        department = topicHotel
    elif user_obj['propType'] == 'Restaurant':
        department = topicRestaurant
    return department


def hodDetails():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city = user_obj['City_Name']
    if user_obj['propType'] == 'Hotel':
        al = app.config['DEPTHOTEL_COLLECTION'].find({"Name": name, "Place": place, "City": city})
        return json.loads(json_util.dumps(al))
    elif user_obj['propType'] == 'Restaurant':
        al = app.config['DEPTRESTAURANT_COLLECTION'].find({"Name": name, "Place": place, "City": city})
        return json.loads(json_util.dumps(al))


def saveHodData(dept, hodname, hodemail):
    connection = get_collection()
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    try:
        state = user_obj['City']
    except:
        state = "Karnataka"
    try:
        country = user_obj['City']
    except:
        country = "India"
    if city_all == "True":
        place = city
    try:
        connection.update({"Dept": dept, "Name": name, "Place": place, "City": city},
                          {"HeadName": hodname, "HeadEmail": hodemail, "Dept": dept, "Name": name, "Place": place,
                           "City": city, "State": state, "Country": country}, upsert=True)
        print("HOD's Details are Saved")
        recipients = tech_recepients
        esubject = "Head of Department's Details updated on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for " + name + ", " + place + ", " + city + "(" + dept + ")"
        ebody = "Details are, \nName: " + hodname + "\nEmail: " + hodemail
        ebody = ebody + "\n\nRepusight Support."
        # send_mail(recipients, esubject, ebody)
        status = "Success"
        return status
    except Exception as e:
        print("HOD's Details are not saved")
        recipients = tech_recepients
        esubject = "Error while updating HOD's Details on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p")
        ebody = "For " + name + ", " + place + ", " + city + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\n\nRepusight Support."
        # send_mail(recipients, esubject, ebody)
        status = "Error"
        return status
