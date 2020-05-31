from app import app
from flask import session
import datetime as dtm
from flask_mail import Mail, Message

DEBUG = True

app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.zoho.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='support@repusight.com',
    MAIL_PASSWORD='repusight'

))
# MAIL_USERNAME = 'info@repusight.com',
# MAIL_PASSWORD = 'reddys_1'
# MAIL_USERNAME = 'offers@repusight.com',
# MAIL_PASSWORD = 'test1234'


mail = Mail(app)


def send_mail(recipients, eSubject, eBody):
    msg = Message(eSubject, sender="support@repusight.com", recipients=recipients, body=eBody)

    mail.send(msg)


def send_mail_campaign(recipients, eSubject, eBody, eCc, eFiles):
    # msg = Message(eSubject, sender="support@repusight.com", recipients=recipients, body=eBody, cc=eCc)
    msg = Message(eSubject, sender="offers@repusight.com", recipients=recipients, cc=eCc)
    msg.body = eBody
    msg.html = eBody

    # if eFiles is not None:
    #     for f in eFiles:
    #         #mime = magic.Magic(mime=True)
    #         #with app.open_resource(f['fpath']) as fp:
    #         #with open(f['fpath'], 'rb') as fp:
    #         with open(f['name'], 'rb') as fp:
    #             #contenttype = mime.from_file(f)
    #             #msg.attach(f, contenttype, fp.read())
    #             #msg.attach(filename=f['fname'], content_type=f['ftype'], disposition='attachment', data=fp.read())
    #             msg.attach(f['fname'], f['ftype'], fp.read())
    #             print(f['fname'], f['ftype'])
    #     #print(msg)

    # mail.connect()
    mail.send(msg)

    user_obj = session.get('user', None)
    username = user_obj['username']
    savedon = dtm.datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    try:
        app.config['SAVEDEMAILDATA_COLLECTION'].update(
            {"username": username, "recipients": recipients, "eSubject": eSubject, "eBody": eBody, "eCc": eCc},
            {'$set': {"Name": user_obj['hotel'], "Place": user_obj['Place'], "City_Name": user_obj['City_Name'],
                      "recipients": recipients, "eSubject": eSubject, "eBody": eBody, "eCc": eCc, "sent": "Yes",
                      "savedOn": savedon}}, upsert=True)
    except Exception as e:
        print(e)


def saveEmailData(recipients, eSubject, eBody, eCc, eFiles):
    user_obj = session.get('user', None)
    username = user_obj['username']
    savedon = dtm.datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    try:
        app.config['SAVEDEMAILDATA_COLLECTION'].update({"username": username}, {
            '$set': {"Name": user_obj['hotel'], "Place": user_obj['Place'], "City_Name": user_obj['City_Name'],
                     "recipients": recipients, "eSubject": eSubject, "eBody": eBody, "eCc": eCc, "sent": "No",
                     "savedOn": savedon}}, upsert=True)
    except Exception as e:
        print(e)


def emailDetails():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city = user_obj['City_Name']
    data = []
    emailDtl_count = app.config['SAVEDEMAILDATA_COLLECTION'].find(
        {'Name': name, "Place": place, "City_Name": city, "sent": "No"}).count()
    if emailDtl_count != 0:
        emailDtl = list(app.config['SAVEDEMAILDATA_COLLECTION'].find(
            {'Name': name, "Place": place, "City_Name": city, "sent": "No"}))
        data.append({'recipients': str(emailDtl[0]['recipients']).replace('[', '').replace(']', '').replace("'", ""),
                     'eSubject': emailDtl[0]['eSubject'],
                     'eCc': str(emailDtl[0]['eCc']).replace('[', '').replace(']', '').replace("'", ""),
                     'eBody': emailDtl[0]['eBody'], 'Name': emailDtl[0]['Name'], 'Place': emailDtl[0]['Place'],
                     'City_Name': emailDtl[0]['City_Name'], 'username': emailDtl[0]['username']})
    else:
        data.append({'recipients': "", 'eSubject': "", 'eCc': "", 'eBody': "",
                     'Name': "", 'Place': "", 'City_Name': "", 'username': ""})
    return data
