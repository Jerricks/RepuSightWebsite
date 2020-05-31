from app import app
from flask import session
import datetime as dtm
import json
from bson import json_util
from bson.objectid import ObjectId
from .model_email import send_mail

topicHotel = ['Food', 'Service', 'Value', 'Ambience', 'Cleanliness', 'Amenities', 'Hospitality', 'Location',
              'Front-Desk', 'Room']

topicRestaurant = ['Taste', 'Variety', 'Drinks', 'Service', 'Value', 'Hygiene', 'Ambience', 'Hospitality', 'Comforts',
                   'Entertainment']


def topics():
    user_obj = session.get('user', None)
    if user_obj['propType'] == 'Hotel':
        choice = topicHotel
    elif user_obj['propType'] == 'Restaurant':
        choice = topicRestaurant
    return choice


def getDeptHead(department, name, place, city):
    user_obj = session.get('user', None)
    deptData = []
    if user_obj['propType'] == 'Hotel':
        data = list(
            app.config['DEPTHOTEL_COLLECTION'].find({"Name": name, "Place": place, "City": city, "Dept": department}))
    elif user_obj['propType'] == 'Restaurant':
        data = list(app.config['DEPTRESTAURANT_COLLECTION'].find(
            {"Name": name, "Place": place, "City": city, "Dept": department}))
    deptData.append({"recipients": [data[0]['HeadEmail'], user_obj['email']], "headname": data[0]['HeadName'],
                     "heademail": data[0]['HeadEmail']})
    return deptData


def allTicketDetails():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if city_all == "True":
        place = city
    data = []
    ticket_open = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Open"})
    ticket_closed = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Closed"})
    ticket_count = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place}).count()
    openTicket_count = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Open"}).count()
    closedTicket_count = app.config['TICKET_COLLECTION'].find(
        {'Name': name, "Place": place, "Status": "Closed"}).count()
    data.append({"ticket_open": json.loads(json_util.dumps(ticket_open)),
                 "ticket_closed": json.loads(json_util.dumps(ticket_closed)), 'ticket_count': ticket_count,
                 'openTicket_count': openTicket_count, 'closedTicket_count': closedTicket_count})
    return data


def addTicket(department, severity, duedate, descriptions):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if city_all == "True":
        place = city
    deptHeadData = getDeptHead(department, name, place, city)
    try:
        assigneddate = dtm.datetime.strptime(str(dtm.date.today()), '%Y-%m-%d').strftime('%d-%m-%Y')
        app.config['TICKET_COLLECTION'].insert_one(
            {"Assigned_Date": assigneddate, "Assigned_To": department, "Description": descriptions, "Due_Date": duedate,
             "Name": name, "Place": place, "Severity": severity, "Status": "Open"})
        print("Ticket created.")
        esubject = "Ticket Added for " + department + " on " + dtm.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        # recipients = ["niki.upadhyay@repusight.com"]
        recipients = deptHeadData[0]['recipients']
        # ebody = "Assigned To: " + department + "\n"
        # ebody = ebody + "Assigned on: " + dtm.datetime.strptime(str(dtm.date.today()), '%Y-%m-%d').strftime('%d %b, %Y') + "\n"
        # ebody = ebody + "Due Date: " + dtm.datetime.strptime(str(duedate), '%Y-%m-%d').strftime('%d %b, %Y') + "\n"
        # ebody = ebody + "Having " + severity + " Priority" + "\n"
        # ebody = ebody + "Please do have look on, \n\n" + descriptions + "\n\n"
        # ebody = ebody + "\n\n\nThank You, \nRepusight Support"
        ebody = "Ticket Overivew: \n\nDepartment : " + department + "\nPriority : " + severity + "\nDue Date : " + dtm.datetime.strptime(
            str(duedate), '%d-%m-%Y').strftime('%d %b, %Y')
        ebody = ebody + "\nCreated On : " + dtm.datetime.strptime(str(dtm.date.today()), '%Y-%m-%d').strftime(
            '%d %b, %Y') + "\n"
        ebody = ebody + "\nCreator : " + user_obj['managername'] + " [" + user_obj['email'] + "] \nAssigned to : " + \
                deptHeadData[0]['headname'] + " [" + deptHeadData[0]['heademail'] + "]"
        ebody = ebody + "\n\n" + descriptions + "\n\n\nThank You, \nRepusight Support."
        send_mail(recipients, esubject, ebody)
        ticket_open = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Open"})
        ticket_closed = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Closed"})
        ticket_count = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place}).count()
        openTicket_count = app.config['TICKET_COLLECTION'].find(
            {'Name': name, "Place": place, "Status": "Open"}).count()
        closedTicket_count = app.config['TICKET_COLLECTION'].find(
            {'Name': name, "Place": place, "Status": "Closed"}).count()
        return json.dumps({"ticket_open": json.loads(json_util.dumps(ticket_open)),
                           "ticket_closed": json.loads(json_util.dumps(ticket_closed)), 'ticket_count': ticket_count,
                           'openTicket_count': openTicket_count, 'closedTicket_count': closedTicket_count})
    except Exception as e:
        print(e)
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error in Adding Ticket (Support) on " + dtm.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e) + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
        ticket_open = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Open"})
        ticket_closed = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place, "Status": "Closed"})
        ticket_count = app.config['TICKET_COLLECTION'].find({'Name': name, "Place": place}).count()
        openTicket_count = app.config['TICKET_COLLECTION'].find(
            {'Name': name, "Place": place, "Status": "Open"}).count()
        closedTicket_count = app.config['TICKET_COLLECTION'].find(
            {'Name': name, "Place": place, "Status": "Closed"}).count()
        return json.dumps({"ticket_open": json.loads(json_util.dumps(ticket_open)),
                           "ticket_closed": json.loads(json_util.dumps(ticket_closed)), 'ticket_count': ticket_count,
                           'openTicket_count': openTicket_count, 'closedTicket_count': closedTicket_count})


def closeTicket(data):
    try:
        user_obj = session.get('user', None)
        app.config['TICKET_COLLECTION'].update({"_id": ObjectId(data)}, {'$set': {"Status": "Closed"}})
        print("Ticket is closed.")
        emaildata = list(app.config['TICKET_COLLECTION'].find({"_id": ObjectId(data)}))
        department = emaildata[0]['Assigned_To']
        duedate = emaildata[0]['Due_Date']
        severity = emaildata[0]['Severity']
        descriptions = emaildata[0]['Description']
        assignedon = emaildata[0]['Assigned_Date']
        name = emaildata[0]['Name']
        place = emaildata[0]['Place']
        deptHeadData = getDeptHead(department, name, place, user_obj['City_Name'])
        esubject = "Ticket Closed for " + department + " on " + dtm.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        # recipients = ["niki.upadhyay@repusight.com"]
        recipients = deptHeadData[0]['recipients']
        # ebody = "Assigned To: " + department + "\n"
        # ebody = ebody + "Assigned on: " + dtm.datetime.strptime(str(assignedon), '%d-%m-%Y').strftime('%d %b, %Y') + "\n"
        # ebody = ebody + "Due Date: " + dtm.datetime.strptime(str(duedate), '%d-%m-%Y').strftime('%d %b, %Y') + "\n"
        # ebody = ebody + "Having " + severity + " Priority" + "\n"
        # ebody = ebody + "Please do have look on, \n\n" + descriptions + "\n\n"
        # ebody = ebody + "\n\n\nThank You, \nRepusight Support"
        ebody = "Ticket Overivew: \n\nDepartment : " + department + "\nPriority : " + severity + "\nDue Date : " + dtm.datetime.strptime(
            str(duedate), '%d-%m-%Y').strftime('%d %b, %Y')
        ebody = ebody + "\nCreated On : " + dtm.datetime.strptime(str(assignedon), '%d-%m-%Y').strftime(
            '%d %b, %Y') + "\n"
        ebody = ebody + "\nCreator : " + user_obj['managername'] + " [" + user_obj['email'] + "] \nAssigned to : " + \
                deptHeadData[0]['headname'] + " [" + deptHeadData[0]['heademail'] + "]"
        ebody = ebody + "\n\n" + descriptions + "\n\n\nThank You, \nRepusight Support."
        send_mail(recipients, esubject, ebody)
        return json.dumps({"response": "updated"})
    except Exception as e:
        print(e)
        emaildata = list(app.config['TICKET_COLLECTION'].find({"_id": ObjectId(data)}))
        name = emaildata[0]['Name']
        place = emaildata[0]['Place']
        objid = emaildata[0]["_id"]
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error in Closing Ticket (Support) on " + dtm.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        ebody = "For " + name + ", " + place + " (ObjectId- " + str(objid) + ")\nSome error has occured: \n" + str(
            e) + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
        return json.dumps({"response": "not updated"})


def removeTicket(data):
    try:
        user_obj = session.get('user', None)
        emaildata = list(app.config['TICKET_COLLECTION'].find({"_id": ObjectId(data)}))
        app.config['TICKET_COLLECTION'].remove({"_id": ObjectId(data)})
        print("Ticket is removed.")
        department = emaildata[0]['Assigned_To']
        duedate = emaildata[0]['Due_Date']
        severity = emaildata[0]['Severity']
        descriptions = emaildata[0]['Description']
        assignedon = emaildata[0]['Assigned_Date']
        name = emaildata[0]['Name']
        place = emaildata[0]['Place']
        deptHeadData = getDeptHead(department, name, place, user_obj['City_Name'])
        esubject = "Ticket Removed for " + department + " on " + dtm.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        # recipients = ["niki.upadhyay@repusight.com"]
        recipients = deptHeadData[0]['recipients']
        # ebody = "Assigned To: " + department + "\n"
        # ebody = ebody + "Assigned on: " + dtm.datetime.strptime(str(assignedon), '%d-%m-%Y').strftime(
        #     '%d %b, %Y') + "\n"
        # ebody = ebody + "Due Date: " + dtm.datetime.strptime(str(duedate), '%d-%m-%Y').strftime('%d %b, %Y') + "\n"
        # ebody = ebody + "Having " + severity + " Priority" + "\n"
        # ebody = ebody + "Please do have look on, \n\n" + descriptions + "\n\n"
        # ebody = ebody + "\n\n\nThank You, \nRepusight Support"
        ebody = "Ticket Overivew: \n\nDepartment : " + department + "\nPriority : " + severity + "\nDue Date : " + dtm.datetime.strptime(
            str(duedate), '%d-%m-%Y').strftime('%d %b, %Y')
        ebody = ebody + "\nCreated On : " + dtm.datetime.strptime(str(assignedon), '%d-%m-%Y').strftime(
            '%d %b, %Y') + "\n"
        ebody = ebody + "\nCreator : " + user_obj['managername'] + " [" + user_obj['email'] + "] \nAssigned to : " + \
                deptHeadData[0]['headname'] + " [" + deptHeadData[0]['heademail'] + "]"
        ebody = ebody + "\n\n" + descriptions + "\n\n\nThank You, \nRepusight Support."
        send_mail(recipients, esubject, ebody)
        return json.dumps({"response": "removed"})
    except Exception as e:
        print(e)
        emaildata = list(app.config['TICKET_COLLECTION'].find({"_id": ObjectId(data)}))
        name = emaildata[0]['Name']
        place = emaildata[0]['Place']
        objid = emaildata[0]["_id"]
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error in Removing Ticket (Support) on " + dtm.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        ebody = "For " + name + ", " + place + " (ObjectId- " + objid + ")\nSome error has occured: \n" + str(
            e) + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
        return json.dumps({"response": "not removed"})


def allEmailDetails():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if city_all == "True":
        place = city
    data = []
    total_campaign = app.config['SAVEDEMAILDATA_COLLECTION'].find(
        {'Name': name, "Place": place, "City_Name": city, "sent": "Yes"}).count()
    total_recipient = 0
    s = set()
    subdata = []
    al = list(
        app.config['SAVEDEMAILDATA_COLLECTION'].find({'Name': name, "Place": place, "City_Name": city, "sent": "Yes"}))
    for ele in al:
        total_recipient += (len(ele['eCc']) + len(ele['recipients']))
        s.update(ele['eCc'])
        s.update(ele['recipients'])
    unique_subscrb = len(s)
    al1 = list(
        app.config['SAVEDEMAILDATA_COLLECTION'].find({'Name': name, "Place": place, "City_Name": city, "sent": "Yes"}))
    al1_final = sorted(al1, key=lambda x: dtm.datetime.strptime(x['savedOn'], '%d-%m-%Y %H:%M:%S'), reverse=True)
    for ele in al1_final[0:5]:
        subdata.append(
            {"campaignName": ele['eSubject'], "campaignRecipient": (len(ele['eCc']) + len(ele['recipients'])),
             "sentOn": dtm.datetime.strptime(ele['savedOn'], '%d-%m-%Y %H:%M:%S').strftime("%d %b, %Y")})
    data.append({"total_campaign": json.loads(json_util.dumps(total_campaign)),
                 "recipient": json.loads(json_util.dumps(total_recipient)),
                 "unique_subscrb": json.loads(json_util.dumps(unique_subscrb)),
                 "emaildlt": json.loads(json_util.dumps(subdata))})
    return data


def allSmsDetails():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if city_all == "True":
        place = city
    data = []
    total_campaign = app.config['SMSDATA_COLLECTION'].find({'Sender': name, "Place": place, "City": city}).count()
    al = list(app.config['SMSDATA_COLLECTION'].find({'Sender': name, "Place": place, "City": city}))
    al_final = sorted(al, key=lambda x: x['Date'].strftime("%d %b, %Y"), reverse=True)
    subdata = []
    for ele in al_final:
        subdata.append(
            {"campaignName": ele['CampaignName'], "campaignRecipient": ele['Number'], "message": ele['Message'],
             "sentOn": ele['Date'].strftime("%d %b, %Y")})
    data.append(
        {"total_campaign": json.loads(json_util.dumps(total_campaign)), "smsdtl": json.loads(json_util.dumps(subdata))})
    return data
