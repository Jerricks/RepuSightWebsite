from app import app
import urllib.request  # Python URL functions
import json
import datetime
from flask import session

authkey = app.config["MSG_TOKEN"]  # Your authentication key.
sender = "OFFERS"  # Sender ID,While using route4 sender id should be 6 characters long.
route = 4  # Define route
url = "https://control.msg91.com/api/sendhttp.php"  # API URL


def msg91(message, mobiles, campaignname):
    try:
        # Prepare you post parameters
        values = {
            'authkey': authkey,
            'mobiles': mobiles,
            'message': message,
            'sender': sender,
            'route': route,
            'response': 'json'
        }
        user_obj = session.get('user', None)
        name = user_obj['hotel']
        place = user_obj['Place']
        city = user_obj['City_Name']
        username = user_obj['username']
        postdata = urllib.parse.urlencode(values).encode("utf-8")  # URL encoding the data here.
        req = urllib.request.Request(url, postdata)
        response = urllib.request.urlopen(req)
        output = json.loads(response.read().decode('utf-8'))  # Get Response
        if output['type'] == "success":
            app.config['SMSDATA_COLLECTION'].insert_one(
                {"username": username, "Number": mobiles, "Message": message, "Date": datetime.datetime.now(),
                 "Sender": name, "Place": place, "City": city, "CampaignName": campaignname})
            status = "Message sent successfully!!"
    except Exception as e:
        print(e)
        status = "Something went wrong! Please try again later."
    return status
