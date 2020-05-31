import flask
from app import app, lm
from flask import request, redirect, render_template, url_for, abort, session, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm, SignupForm, ForgetPasswordForm
from .user import User
from .model_summary import *
from .model_review import sources, getReview, summaryKeywords
from .model_source import allSourceData
from .model_socialmedia import facebook, twitter, instagram
from .model_ca import competitive_index
from .model_support import topics, addTicket, allTicketDetails, closeTicket, removeTicket, allEmailDetails, \
    allSmsDetails
from .model_email import send_mail, send_mail_campaign, saveEmailData, emailDetails
from .model_guestIQ import guestData
from .model_sms import msg91
from .model_credentials import saveData, sourcesList, replyCredDetails, socialmediaList, smKeyword, saveDataSM
from .model_deptHead import check_proptype, hodDetails, saveHodData
import json, time
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError
import datetime
from dateutil import tz
from bson.objectid import ObjectId
from bson import json_util
from pymongo.errors import ServerSelectionTimeoutError

tech_recepients = ["sanket.mokashi@repusight.com"]


# --- error redirects-----
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404


@app.errorhandler(ServerSelectionTimeoutError)
def database_error(e):
    app.logger.error('Database disconnected ERROR: {}'.format(e))
    abort(500)
    return render_template('500-error.html')


@app.errorhandler(500)
def server_error(e):
    app.logger.error(msg='Server error {}'.format(e))
    return render_template('500-error.html'), 500


# ---------- Login / Logout / Session Maintain -------------


@app.route('/')
def home():
    return redirect(url_for("login"))


@app.before_request
def set_session():
    import flask_login
    flask.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=20)
    flask.session.modified = True
    flask.g.user = flask_login.current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ""
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data) and user[u'status'] == True:
            user_obj = User(user['_id'])
            login_user(user_obj, remember=False)
            session['logged_in'] = True
            session['user'] = user
            # flash("Logged in successfully!", category='success')
            print("Logged in successfully!")
            if user['role'] == 'adminPanel':
                return redirect(request.args.get("next") or url_for("sources_crawler"))
            else:
                return redirect(request.args.get("next") or url_for("summary"))
        else:
            # flash("Wrong username or password!", category='error')
            error = "Wrong username or password!"
            # print("Wrong username or password!")
    return render_template('login.html', title='login', form=form, error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    return redirect(url_for('login'))


@lm.user_loader
def load_user(username):
    u = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])


@app.route('/user', methods=["POST"])
def user():
    user_obj = session.get('user', None)
    return json.dumps(user_obj)


# ---------- Login / Logout / Session Maintain -------------

# ---------- Pro Dashboard -------------


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    error = ""
    # temp = list(app.config['AREAS_COLLECTION'].find({"city": "Bangalore"}, {"area": 1, "_id": 0}))
    # data = []
    # choicesarray = [("None", "--Select--")]
    # for ele in temp:
    #     data.append(ele['area'])
    # data = sorted(data)
    # for d in data:
    #     choicesarray.append((d, d))
    # form.propLocat.choices = choicesarray

    # There is no dependency till now, it can be applied later on.

    # temp_country = list(app.config['COUNTRY_COLLECTION'].find({"Name": 1, "_id": 0}))
    temp_country = list(app.config['COUNTRY_COLLECTION'].find({"Status": "Active"}))
    data_country = []
    choicesarray_country = [("None", "--Select--")]
    for ele in temp_country:
        data_country.append(ele['Name'])
    for d in data_country:
        choicesarray_country.append((d, d))
    form.propLocatCountry.choices = choicesarray_country

    # temp_state = list(app.config['STATE_COLLECTION'].find({"Name": 1, "_id": 0}))
    temp_state = list(app.config['STATE_COLLECTION'].find({"Status": "Active"}))
    data_state = []
    choicesarray_state = [("None", "--Select--")]
    for ele in temp_state:
        # data_state.append(ele['Name'])
        data_state.append({"Name": ele['Name'], "Country": ele['Country']})
    for d in data_state:
        # choicesarray_state.append((d, d))
        choicesarray_state.append((d['Name'], d['Name'] + ", " + d['Country']))
    form.propLocatState.choices = choicesarray_state

    # temp_city = list(app.config['CITY_COLLECTION'].find({"Name": 1, "_id": 0}))
    temp_city = list(app.config['CITY_COLLECTION'].find({"Status": "Active"}))
    data_city = []
    choicesarray_city = [("None", "--Select--")]
    for ele in temp_city:
        data_city.append({"Name": ele['Name'], "State": ele['State'], "Country": ele['Country']})
    for d in data_city:
        choicesarray_city.append((d['Name'], d['Name'] + ", " + d['State'] + ", " + d['Country']))
    form.propLocatCity.choices = choicesarray_city

    # temp_area = list(app.config['AREAS_COLLECTION'].find({"Name": 1, "_id": 0}))
    temp_area = list(app.config['AREAS_COLLECTION'].find({"Status": "Active"}))
    data_area = []
    choicesarray_area = [("None", "--Select--")]
    for ele in temp_area:
        data_area.append({"Name": ele['Name'], "City": ele['City'], "State": ele['State'], "Country": ele['Country']})
    for ele in temp_city:
        data_area.append({"Name": ele['Name'], "City": ele['Name'], "State": ele['State'], "Country": ele['Country']})
    for d in data_area:
        choicesarray_area.append((d['Name'], d['Name'] + ", " + d['City'] + ", " + d['State'] + ", " + d['Country']))
    form.propLocat.choices = choicesarray_area

    if request.method == 'POST' and form.validate_on_submit():
        pass_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        try:
            app.config['REGISTEREDUSERS_COLLECTION'].insert_one(
                {"_id": form.username.data, "username": form.username.data, "password": pass_hash,
                 "role": form.designation.data, "hotel": form.propName.data, "Place": form.propLocat.data,
                 "email": form.email.data, "status": "true", 'phone': form.mobile.data, "propType": form.propType.data,
                 "managername": form.name.data, "country": form.propLocatCountry.data,
                 "state": form.propLocatState.data,
                 "City_Name": form.propLocatCity.data, "Logo": "", "City": "False", "group": []})
            app.config['SOCIALMEDIADATA_COLLECTION'].insert_one(
                {"_id": form.username.data, "hotel": form.propName.data, "Place": form.propLocat.data, "fbkeyword": "",
                 "instagramkeyword": "", 'twitterkeyword': "", "country": form.propLocatCountry.data,
                 "state": form.propLocatState.data,
                 "City_Name": form.propLocatCity.data})
            print("User created.")
            recipients = tech_recepients
            esubject = "New User is created on " + datetime.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
            ebody = "Please update other required fields in the database to make sure user do not face any issue while using the Dashboard. \n\n"
            ebody = ebody + "1.\tCheck 'Place' & 'hotel' fields."
            ebody = ebody + "\n2.\tInsert 'Logo'(logo of the property), 'City'('True' if grouping like Ammi's Biryani is required, else 'False'), 'City_Name'."
            ebody = ebody + "\n3.\t'group' (For Competitive Analysis. If it need to blank then insert '[ ]', else insert proper group with checking on Name & Place of the Competitors-Refer Sarovar's grouping for the same)."
            ebody = ebody + "\n4.\tGet all required credentials to make comment response possible. (Collections: replyLoginCredentials, zmEntityId)"
            ebody = ebody + "\n5.\tGet all department head's name & email id. (Collections: departmentHeadsHotel, departmentHeadsRestaurant)"
            ebody = ebody + "\n6.\tUpdate Social Media Keywords. (Collection: socialMediaData)"
            ebody = ebody + "\n\nProperty Type : " + form.propType.data
            ebody = ebody + "\nProperty Name : " + form.propName.data
            ebody = ebody + "\nProperty Address : " + form.propAdder.data
            ebody = ebody + "\nProperty Country : " + form.propLocatCountry.data
            ebody = ebody + "\nProperty State : " + form.propLocatState.data
            ebody = ebody + "\nProperty City : " + form.propLocatCity.data
            ebody = ebody + "\nProperty Area : " + form.propLocat.data
            ebody = ebody + "\nUsername for the Property : " + form.username.data
            ebody = ebody + "\nPassword for the Property : " + form.password.data
            ebody = ebody + "\nEmail : " + form.email.data
            ebody = ebody + "\nContanct No. : " + form.mobile.data
            ebody = ebody + "\n\nRepusight Support."
            send_mail(recipients, esubject, ebody)
            return redirect(url_for("login"))
        except DuplicateKeyError:
            print("User already created! This is duplicate Entry.")
            return redirect(url_for("login"))
    elif request.method == 'POST' and form.validate_on_submit() == False:
        error = "Please fill all the required fields"
    return render_template('signup.html', title="signup", form=form, error=error)


@app.route('/forgotpsw', methods=['GET', 'POST'])
def forgotpsw():
    form = ForgetPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and user[u'status'] == u'true':
            pass_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            try:
                app.config['REGISTEREDUSERS_COLLECTION'].update({"_id": form.username.data},
                                                                {'$set': {"password": pass_hash}})
                # flash("Password updated.", category='message')
                print("Password updated.")
                recipients = tech_recepients
                esubject = "Password updated on " + datetime.datetime.now().strftime(
                    "%d %b, %Y %I:%M:%S %p") + " for " + form.username.data
                ebody = "New Password for " + form.username.data + " is, \n\n\t" + form.password.data
                ebody = ebody + "\n\nRepusight Support."
                send_mail(recipients, esubject, ebody)
                recipients1 = [user[u'email']]
                esubject1 = "Your Password has been updated"
                ebody1 = "New Password set on " + datetime.datetime.now().strftime(
                    "%d %b, %Y %I:%M:%S %p") + " is,\n" + form.password.data
                ebody1 = ebody1 + "\n\n\nThank You, Repusight Support."
                send_mail(recipients1, esubject1, ebody1)
                return redirect(url_for("login"))
            except Exception as e:
                # flash("Password is not updated.", category='error')
                print("Password is not updated.")
                recipients = tech_recepients
                esubject = "Error while updating password on " + datetime.datetime.now().strftime(
                    "%d %b, %Y %I:%M:%S %p")
                ebody = "For " + user[u'hotel'] + ", " + user[u'Place'] + "\nSome error has occured: \n" + str(e)
                ebody = ebody + "\n\n\nRepusight Support."
                send_mail(recipients, esubject, ebody)
    return render_template('forgot-password.html', title="forgetpsw", form=form)


@app.route('/summary')
@login_required
def summary():
    template = render_template('summary.html', hotelDetails=hotelDetails(), summaryCA=summaryCA())
    return template


@app.route('/respond', methods=["POST"])
def get_reply():
    if request.method == 'POST':
        filt = request.get_json()
        print(filt)
        result = app.config['REPLIES_COLLECTION'].insert({'ReviewerName': filt['rname'], 'ReplyText': filt['message'],
                                                          'CommentDate': filt['rdate'], 'reviewID': filt['reviewId'],
                                                          'CommentId': filt['oid'], 'PropertyLocation': filt['place'],
                                                          'PropertyName': filt['hotel'], 'RepliedStatus': None,
                                                          'city': "Bangalore", "Source": filt['channel']})
        if type(result) == ObjectId:
            return json.dumps({'msg': 'Success'})
        else:
            return json.dumps({'Status': 'Error'})


@app.route('/summaryData', methods=['GET', 'POST'])
@login_required
def summaryData():
    user_obj = session.get('user', None)
    name = user_obj["hotel"]
    uPlace = user_obj["Place"]
    uYear = datetime.datetime.today().year
    if request.method == "POST":
        filter = request.get_json()
        if filter is not None:
            place = filter['place']
            year = filter['year']
            if filter['startdt'] != "" and filter['enddt'] != "":
                start = int(time.mktime(datetime.datetime.strptime(filter['startdt'], '%d/%m/%Y').timetuple()))
                end = int(time.mktime(datetime.datetime.strptime(filter['enddt'], '%d/%m/%Y').timetuple()))
            else:
                thirtydays = datetime.date.today() - datetime.timedelta(30)
                start = int(thirtydays.strftime("%s"))
                end = int(datetime.date.today().strftime("%s"))
            return json.dumps({"placeList": getPlaceList(), "defaultplace": place,
                               "summarydata": getSummaryData(place=place, year=year, startdate=start, enddate=end),
                               "defaultyear": year})
    else:
        thirtydays = datetime.date.today() - datetime.timedelta(30)
        start = int(thirtydays.strftime("%s"))
        end = int(datetime.date.today().strftime("%s"))
        if name in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]:
            return json.dumps({"placeList": getPlaceList(), "defaultplace": "-- All --",
                               "summarydata": getSummaryData(place="-- All --", year=uYear, startdate=start,
                                                             enddate=end), "defaultyear": uYear})
        else:
            return json.dumps(
                {"placeList": getPlaceList(), "defaultplace": uPlace,
                 "summarydata": getSummaryData(place=uPlace, year=uYear, startdate=start, enddate=end),
                 "defaultyear": uYear})


@app.route('/review', methods=['GET'])
@login_required
def review():
    getRe = getReview()
    return render_template("review.html", hotelDetails=hotelDetails(), sources=sources(),
                           summaryKeywords=summaryKeywords(), getReview=getReview(), topics=topics())


@app.route('/review/reply-fb/<revno>')
@login_required
def fb_replier(revno):
    pass


@app.route('/source', methods=['GET'])
@login_required
def source():
    return render_template("source.html", hotelDetails=hotelDetails(), sourceData=allSourceData())


@app.route('/socialmedia', methods=['GET'])
@login_required
def socialmedia():
    return render_template("socialMedia.html", hotelDetails=hotelDetails(), facebook=facebook(), twitter=twitter(),
                           instagram=instagram())


# <....... Competitive Analysis Page ......>
'''@app.route('/competitiveAnalysis', methods=['GET'])
@login_required
def competitiveAnalysis():
    return render_template("competitiveAnalysis.html", hotelDetails=hotelDetails())
'''


@app.route('/competitiveAnalysis')
@login_required
def sas():
    hotss = hotelDetails()
    return render_template('ca.html', hotelDetails=hotss)


@app.route('/CA/<topic>', methods=['POST'])
def competitivepertopic(topic):
    data = request.get_json()
    user_obj = session.get('user', None)
    if data != {}:
        startdate = int(time.mktime(datetime.datetime.strptime(data['startdate'], '%d/%b/%Y').timetuple()))
        enddate = int(time.mktime(datetime.datetime.strptime(data['enddate'], '%d/%b/%Y').timetuple()))
        values = competitive_index(startdate, enddate, topic)
        return json.dumps({'type': user_obj['propType'], "values": values})
    else:
        thirtydays = datetime.date.today() - datetime.timedelta(30)
        start = int(thirtydays.strftime("%s"))
        end = int(datetime.date.today().strftime("%s"))
        return json.dumps({'type': user_obj['propType'], "values": competitive_index(start, end, topic)})


'''
@app.route('/competitiveData', methods=['GET', 'POST'])
@login_required
def competitiveData():
    thirtydays = datetime.date.today() - datetime.timedelta(30)
    start = int(thirtydays.strftime("%s"))
    end = int(datetime.date.today().strftime("%s"))
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            startdate = int(time.mktime(datetime.datetime.strptime(filter['startdate'], '%d/%m/%Y').timetuple()))
            enddate = int(time.mktime(datetime.datetime.strptime(filter['enddate'], '%d/%m/%Y').timetuple()))
            return json.dumps({"values": competitive_index(startdate, enddate)})
        else:
            return json.dumps({"values": competitive_index(start, end)})
    else:
        return json.dumps({"values": competitive_index(start, end)})
'''


@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    return render_template("support.html", hotelDetails=hotelDetails())


@app.route('/supportData', methods=["GET", "POST"])
@login_required
def supportData():
    return json.dumps(
        {"topicValues": topics(), 'allTicketDetails': allTicketDetails(), 'allEmailDetails': allEmailDetails(),
         'allSmsDetails': allSmsDetails()})


@app.route('/addticket', methods=["GET", "POST"])
@login_required
def addticket():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            ts = datetime.datetime.strptime(filter['duedate'], "%Y-%m-%dT%H:%M:%S.000Z")
            ts = ts.replace(tzinfo=from_zone)
            duedt = ts.astimezone(to_zone)
            if duedt.month < 10:
                thismonth = "0" + str(duedt.month)
            else:
                thismonth = str(duedt.month)
            duedt1 = str(duedt.day) + "-" + thismonth + "-" + str(duedt.year)
            return addTicket(filter['department'], filter['severity'], duedt1, filter['descriptions'])
        else:
            return print("Nothing to Add")
    else:
        return print("Nothing to Add")


@app.route('/closeticket', methods=["GET", "POST"])
def closeticket():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            return closeTicket(filter['data'])
        else:
            return print("No ticket is selected to update")
    else:
        return print("No ticket is selected to update")


@app.route('/removeticket', methods=["GET", "POST"])
def removeticket():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            return removeTicket(filter['data'])
        else:
            return print("No ticket is selected to remove")
    else:

        return print("No ticket is selected to remove")


@app.route("/guestIQ", methods=["GET", "POST"])
@login_required
def guestIQ():
    return render_template("guestIQ.html", hotelDetails=hotelDetails(), guestData=guestData())


@app.route('/emailPage')
@login_required
def emailPage():
    return render_template('emailPage.html', hotelDetails=hotelDetails())


@app.route('/sendemail', methods=["GET", "POST"])
@login_required
def sendemail():
    user_obj = session.get('user', None)
    sender = user_obj['email']
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            if None in filter['cc']:
                filter['cc'] = [sender]
            else:
                if sender in filter['cc']:
                    filter['cc'] = filter['cc']
                else:
                    filter['cc'].append(sender)
            send_mail_campaign(filter['recipients'], filter['eSubject'], filter['eBody'], filter['cc'],
                               filter['eFiles'])
            return json.dumps({"status": "Email Campaign Sent"})
        else:
            return json.dumps({"status": "Data is not there to be Sent"})
    else:
        return json.dumps({"status": "Nothing to be sent"})


@app.route('/emailsave', methods=["GET", "POST"])
@login_required
def emailsave():
    user_obj = session.get('user', None)
    sender = user_obj['email']
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            if filter is not None:
                if None in filter['cc']:
                    filter['cc'] = [sender]
                else:
                    if sender in filter['cc']:
                        filter['cc'] = filter['cc']
                    else:
                        filter['cc'].append(sender)
            saveEmailData(filter['recipients'], filter['eSubject'], filter['eBody'], filter['cc'], filter['eFiles'])
            return json.dumps({"status": "Draft is saved"})
        else:
            return json.dumps({"status": "Data is not there to be saved"})
    else:
        return json.dumps({"status": "Nothing to be saved"})


@app.route('/emailData', methods=["GET", "POST"])
@login_required
def emailData():
    return json.dumps({'emailDetails': emailDetails()})


@app.route('/smsDetails', methods=["GET", "POST"])
@login_required
def smsDetails():
    if request.method == "POST":
        filter = request.get_json()
        status = msg91(message=filter["message"], mobiles=filter["number"], campaignname=filter["campaignname"])
        return json.dumps({"status": status})


@app.route('/credentials', methods=["GET", "POST"])
@login_required
def credentials():
    return render_template('credentials.html', hotelDetails=hotelDetails(), sourcesList=sourcesList(),
                           socialmediaList=socialmediaList())


@app.route('/fb_login', methods=['POST'])
@login_required
def log_on_fb():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        return json.dumps(data)


@app.route('/credDetails', methods=["GET", "POST"])
@login_required
def credDetails():
    return json.dumps({"CredDetails": replyCredDetails()})


@app.route('/savedatacre', methods=["GET", "POST"])
@login_required
def savedatacre():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            return json.dumps({"response": saveData(filter['user_id'], filter['password'], filter['source'])})
        else:
            print("Nothing to Add")
            return json.dumps({"response": "Error"})
    else:
        print("No Data Available")
        return json.dumps({"response": "Error"})


@app.route('/smDetails', methods=["GET", "POST"])
@login_required
def smDetails():
    return json.dumps({"smDetails": smKeyword()})


@app.route('/savedatasm', methods=["GET", "POST"])
@login_required
def savedatasm():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            return json.dumps({"response": saveDataSM(filter['keyword'], filter['smsource'])})
        else:
            print("Nothing to Add")
            return json.dumps({"response": "Error"})
    else:
        print("No Data Available")
        return json.dumps({"response": "Error"})


@app.route('/changePsw', methods=["GET", "POST"])
def changePsw():
    if request.method == 'POST':
        user_obj = session.get('user', None)
        filter = request.get_json()
        if User.validate_login(user_obj['password'], filter['oldpsw']):
            user = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"_id": filter['curruser']})
            pass_hash = generate_password_hash(filter['newpsw'], method='pbkdf2:sha256')
            try:
                app.config['REGISTEREDUSERS_COLLECTION'].update({"_id": filter['curruser']},
                                                                {'$set': {"password": pass_hash}})
                print("Password changed.")
                recipients = tech_recepients
                esubject = "Password changed on " + datetime.datetime.now().strftime(
                    "%d %b, %Y %I:%M:%S %p") + " for " + filter['curruser']
                ebody = "New Password for " + filter['curruser'] + " is, \n\n\t" + filter['newpsw']
                ebody = ebody + "\n\nRepusight Support."
                send_mail(recipients, esubject, ebody)
                recipients1 = [user[u'email']]
                esubject1 = "Your Password has been changed"
                ebody1 = "New Password set on " + datetime.datetime.now().strftime(
                    "%d %b, %Y %I:%M:%S %p") + " is,\n" + filter['newpsw']
                ebody1 = ebody1 + "\n\n\nThank You, Repusight Support."
                send_mail(recipients1, esubject1, ebody1)
                # return redirect(url_for("summary"))
                resp_update = {"response": "true"}
            except Exception as e:
                print("Password is not changed.")
                recipients = tech_recepients
                esubject = "Error while changing password on " + datetime.datetime.now().strftime(
                    "%d %b, %Y %I:%M:%S %p")
                ebody = "For " + user[u'hotel'] + ", " + user[u'Place'] + "\nSome error has occured: \n" + str(e)
                ebody = ebody + "\n\n\nRepusight Support."
                send_mail(recipients, esubject, ebody)
                resp_update = {"response": "false"}
        else:
            resp_update = {"response": "false"}
        return json.dumps(resp_update)
    else:
        return render_template('changePsw.html', hotelDetails=hotelDetails())


@app.route('/deptHead', methods=["GET", "POST"])
@login_required
def deptHead():
    return render_template('departmentHeads.html', hotelDetails=hotelDetails(), departmentList=check_proptype())


@app.route('/gethodDetails', methods=["GET", "POST"])
@login_required
def gethodDetails():
    return json.dumps({"hodDetails": hodDetails()})


@app.route('/savedatahod', methods=["GET", "POST"])
@login_required
def savedatahod():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            return json.dumps({"response": saveHodData(filter['dept'], filter['hodname'], filter['hodemail'])})
        else:
            print("Nothing to Add")
            return json.dumps({"response": "Error"})
    else:
        print("No Data Available")
        return json.dumps({"response": "Error"})


# ---------- Pro Dashboard -------------

# ---------- Admin Panel -------------


def getSequence(idname):
    sequence = str(app.config['SEQUENCE_COLLECTION'].find_and_modify(query={'collection': 'admin_collection'},
                                                                     update={'$inc': {idname: 1}},
                                                                     fields={idname: 1, '_id': 0}, new=True).get(
        idname))
    return sequence


@app.route('/sources_crawler')
@login_required
def sources_crawler():
    return render_template('sources_crawler.html')


@app.route('/location')
@login_required
def location():
    return render_template('location.html')


@app.route("/addsource", methods=["POST"])
@login_required
def addsource():
    # this defination is used for adding source data

    if request.method == 'POST':
        filter = request.get_json()  # get data send by post request in json format
        if filter is not None:
            dict = {}
            try:
                seq = int(float(getSequence("sourceId")))
                app.config['SOURCES_COLLECTION'].insert_one(
                    {"_id": seq, "Name": filter["sourceName"], "For": filter["propertyType"], "icon": filter["icon"],
                     "insertDate": time.time(), "updateDate": "", "Status": "Active"})  # insert query
                dict["status"] = "Source Added Successfully"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/sourceData", methods=["GET"])
@login_required
def sourceData():
    # get source data from source collection from database
    sourcesData = []
    sourceHotel = []
    sourceRestaurant = []
    try:
        sourcesData = list(app.config['SOURCES_COLLECTION'].find({"Status": "Active"}))
        sourceRestaurant = list(app.config['SOURCES_COLLECTION'].find({"Status": "Active", "For": "Restaurant"}))
        sourceHotel = list(app.config['SOURCES_COLLECTION'].find({"Status": "Active", "For": "Hotel"}))
    except Exception as e:
        print(e)
    return json.dumps({"sourcesData": sourcesData, "sourceHotel": sourceHotel, "sourceRestaurant": sourceRestaurant})


@app.route('/removesource', methods=["GET", "POST"])
@login_required
def removesource():
    # remove source from database
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                # app.config['SOURCES_COLLECTION'].remove({"_id": filter['data']})  # remove query
                app.config['SOURCES_COLLECTION'].update({"_id": filter['data']},
                                                        {"$set": {"Status": "Inactive", "updateDate": time.time()}})
                status = "Removes"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No ticket is selected to remove"
    else:
        status = "No ticket is selected to remove"
    return json.dumps({"status": status})


@app.route("/updatesource", methods=["POST"])
@login_required
def updatesource():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                app.config['SOURCES_COLLECTION'].update({"_id": filter["updateId"]}, {
                    "$set": {"Name": filter["sourceName"], "For": filter["propertyType"], "icon": filter["icon"],
                             "updateDate": time.time()}})
                dict["status"] = "Source Updated Successfully"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/property')
@login_required
def property():
    return render_template('property.html')


@app.route("/addproperty", methods=["POST"])
@login_required
def addproperty():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                seq = int(float(getSequence("propertyId")))
                app.config['PROPERTY_COLLECTION'].insert_one(
                    {"_id": seq, "propertyName": filter["propertyName"], "For": filter["propertyType"],
                     "City": filter["propertyCity"], "Place": filter["propertyPlace"], "Logo": filter["logo"],
                     "source": filter["propertyTypeSource"], "revertURL": filter["url"], "insertDate": time.time(),
                     "updateDate": "", "type": filter['clientType'], "State": filter['state'], "Status": "Active",
                     "Country": filter['country'], "lastCrawl": "", "url1": filter['url1'], "url2": filter['url2']})
                dict["status"] = "Property Added Successfully"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/propertyData", methods=["GET", "POST"])
@login_required
def propertyData():
    try:
        property_Data = list(app.config['PROPERTY_COLLECTION'].find({"Status": "Active"}))
        propertyList = list(set([x["propertyName"] + "," + x["Place"] for x in property_Data]))
        property_Hotel = list(
            app.config['PROPERTY_COLLECTION'].find({"Status": "Active", "For": "Hotel", "type": "Customer"}))
        property_Restaurant = list(
            app.config['PROPERTY_COLLECTION'].find(
                {"Status": "Active", "For": "Restaurant", "type": "Customer"}))
        return json.dumps({"property_Data": property_Data, "propertyList": propertyList,
                           "property_Hotel": property_Hotel, "property_Restaurant": property_Restaurant})
    except Exception as e:
        print(e)
        return json.dumps({"property_Data": [], "propertyList": [], "property_Hotel": [], "property_Restaurant": []})


@app.route('/removeproperty', methods=["GET", "POST"])
def removeproperty():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['PROPERTY_COLLECTION'].update({"_id": filter['data']},
                                                         {"$set": {"Status": "Inactive", "updateDate": time.time()}})
                status = "Removes"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No ticket is selected to remove"
    else:
        status = "No ticket is selected to remove"
    return json.dumps({"status": status})


@app.route("/updateproperty", methods=["POST"])
@login_required
def updateproperty():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                app.config['PROPERTY_COLLECTION'].update({"_id": filter["updateId"]}, {
                    "$set": {"propertyName": filter["propertyName"], "For": filter["propertyType"],
                             "City": filter["propertyCity"], "Place": filter["propertyPlace"], "Logo": filter["logo"],
                             "source": filter["propertyTypeSource"], "revertURL": filter["url"],
                             "updateDate": time.time(), "type": filter['clienttype'], "State": filter['state'],
                             "Country": filter['country'], "url1": filter['url1'], "url2": filter['url2']}})
                dict["status"] = "Property Updated Successfully"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/countryData", methods=["GET"])
@login_required
def countryData():
    try:
        countryData = list(app.config['COUNTRY_COLLECTION'].find({"Status": "Active"}))
    except Exception as e:
        print(e)
    return json.dumps({"countryData": countryData})


@app.route("/addcountry", methods=["POST"])
@login_required
def addcountry():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                seq = int(float(getSequence("countryId")))
                app.config['COUNTRY_COLLECTION'].insert_one(
                    {"_id": seq, "Name": filter["countryName"], "ShortName": filter["countryShortName"],
                     "insertDate": time.time(), "updateDate": "", "Status": "Active"})
                dict["status"] = "Source Added Successfully"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/removecountry', methods=["GET", "POST"])
@login_required
def removecountry():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['COUNTRY_COLLECTION'].update({"_id": filter['data']},
                                                        {"$set": {"Status": "Inactive", "updateDate": time.time()}})
                status = "Country Removed !!"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No country is selected to remove"
    else:
        status = "No country is selected to remove"
    return json.dumps({"status": status})


@app.route("/updatecountry", methods=["POST"])
@login_required
def updatecountry():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                app.config['COUNTRY_COLLECTION'].update({"_id": filter["updateId"]}, {
                    "$set": {"Name": filter["countryName"], "ShortName": filter["countryShortName"],
                             "updateDate": time.time()}})
                dict["status"] = "Country Updated Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/stateData", methods=["GET"])
@login_required
def stateData():
    try:
        stateData = list(app.config['STATE_COLLECTION'].find({"Status": "Active"}))
    except Exception as e:
        print(e)
    return json.dumps({"stateData": stateData})


@app.route("/addstate", methods=["POST"])
@login_required
def addstate():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                seq = int(float(getSequence("stateId")))
                app.config['STATE_COLLECTION'].insert_one(
                    {"_id": seq, "Name": filter["stateName"], "ShortName": filter["stateShortName"],
                     "Country": filter["stateCountry"], "insertDate": time.time(), "updateDate": "",
                     "Status": "Active"})
                dict["status"] = "State Added Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/removestate', methods=["GET", "POST"])
@login_required
def removestate():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['STATE_COLLECTION'].update({"_id": filter['data']},
                                                      {"$set": {"Status": "Inactive", "updateDate": time.time()}})
                status = "State Removed !!"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No state is selected to remove"
    else:
        status = "No state is selected to remove"
    return json.dumps({"status": status})


@app.route("/updatestate", methods=["POST"])
@login_required
def updatestate():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                app.config['STATE_COLLECTION'].update({"_id": filter["updateId"]}, {
                    "$set": {"Name": filter["stateName"], "ShortName": filter["stateShortName"],
                             "Country": filter["stateCountryName"], "updateDate": time.time()}})
                dict["status"] = "State Updated Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/cityData", methods=["GET"])
@login_required
def cityData():
    try:
        cityData = list(app.config['CITY_COLLECTION'].find({"Status": "Active"}))
    except Exception as e:
        print(e)
    return json.dumps({"cityData": cityData})


@app.route("/addcity", methods=["POST"])
@login_required
def addcity():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                seq = int(float(getSequence("cityId")))
                app.config['CITY_COLLECTION'].insert_one(
                    {"_id": seq, "Name": filter["cityName"], "ShortName": filter["cityShortName"],
                     "State": filter["cityState"], "Country": filter["cityCountry"], "insertDate": time.time(),
                     "updateDate": "", "Status": "Active"})
                dict["status"] = "City Added Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/removecity', methods=["GET", "POST"])
@login_required
def removecity():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['CITY_COLLECTION'].update({"_id": filter['data']},
                                                     {"$set": {"Status": "Inactive", "updateDate": time.time()}})
                status = "City Removed !!"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No city is selected to remove"
    else:
        status = "No city is selected to remove"
    return json.dumps({"status": status})


@app.route("/updatecity", methods=["POST"])
@login_required
def updatecity():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                app.config['CITY_COLLECTION'].update({"_id": filter["updateId"]}, {
                    "$set": {"Name": filter["cityName"], "ShortName": filter["cityShortName"],
                             "State": filter["cityStateName"], "Country": filter["cityCountryName"],
                             "updateDate": time.time()}})
                dict["status"] = "City Updated Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/areaData", methods=["GET"])
@login_required
def areaData():
    try:
        areaData = list(app.config['AREAS_COLLECTION'].find({"Status": "Active"}))
    except Exception as e:
        print(e)
    return json.dumps({"areaData": areaData})


@app.route("/addarea", methods=["POST"])
@login_required
def addarea():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                seq = int(float(getSequence("areaId")))
                app.config['AREAS_COLLECTION'].insert_one(
                    {"_id": seq, "Name": filter["areaName"], "ShortName": filter["areaShortName"],
                     "City": filter["areaCity"], "Status": "Active",
                     "State": filter["areaState"], "Country": filter["areaCountry"], "insertDate": time.time(),
                     "updateDate": ""})
                dict["status"] = "City Added Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/removearea', methods=["GET", "POST"])
@login_required
def removearea():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['AREAS_COLLECTION'].update({"_id": filter['data']},
                                                      {"$set": {"Status": "Inactive", "updateDate": time.time()}})
                status = "City Removed !!"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No city is selected to remove"
    else:
        status = "No city is selected to remove"
    return json.dumps({"status": status})


@app.route("/updatearea", methods=["POST"])
@login_required
def updatearea():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                app.config['AREAS_COLLECTION'].update({"_id": filter["updateId"]}, {
                    "$set": {"Name": filter["areaName"], "ShortName": filter["areaShortName"],
                             "City": filter["areaCityName"], "State": filter["areaStateName"],
                             "Country": filter["areaCountryName"], "updateDate": time.time()}})
                dict["status"] = "City Updated Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/replylogincredentials')
@login_required
def replylogincredentials():
    return render_template('replylogincredentials.html')


@app.route("/replyloginData", methods=["GET"])
@login_required
def replyloginData():
    replyloginData = []
    try:
        replyloginData = app.config['REPLYCREDENTIALS_COLLECTION'].find({"Status": "Active"})
    except Exception as e:
        print(e)
    return json.dumps({"replyloginData": json.loads(json_util.dumps(replyloginData))})


@app.route("/addreplyloginData", methods=["GET", "POST"])
@login_required
def addreplyloginData():
    if request.method == 'POST':
        filter = request.get_json()
        print(filter)
        if filter is not None:
            dict = {}
            try:
                app.config['REPLYCREDENTIALS_COLLECTION'].insert_one(
                    {"Name": filter["Name"], "Place": filter["Place"],
                     "City": filter["City"], "State": filter["State"], "Country": filter["Country"],
                     "Channel": filter["Channel"], "ChannelUrl": filter["ChannelUrl"], "UserId": filter["UserId"],
                     "Password": filter["Password"], "backupNo": filter["backupNo"], "Status": "Active"})
                dict["status"] = "Data Added Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/removereplycred', methods=["GET", "POST"])
@login_required
def removereplycred():
    if request.method == 'POST':
        filter = request.get_json()
        data = filter['data']
        if filter is not None:
            try:
                # app.config['REPLYCREDENTIALS_COLLECTION'].update({"_id": ObjectId(data)},
                #                                       {"$set": {"Status": "Inactive"}})
                app.config['REPLYCREDENTIALS_COLLECTION'].remove({"_id": ObjectId(data)})
                status = "Data Removed !!"
            except Exception as e:
                print(e)
                status = "Something went wrong"
        else:
            status = "No data selected to remove"
    else:
        status = "No data selected to remove"
    return json.dumps({"status": status})


@app.route("/updatecredential", methods=["POST"])
@login_required
def updatecredential():
    dict = {}
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['REPLYCREDENTIALS_COLLECTION'].update({"_id": ObjectId(filter["updateId"])}, {
                    "$set": {"Name": filter["Name"], "Place": filter["Place"], "Status": "Active",
                             "City": filter["City"], "State": filter["State"], "Country": filter["Country"],
                             "Channel": filter["Channel"], "ChannelUrl": filter["ChannelUrl"],
                             "UserId": filter["UserId"],
                             "Password": filter["Password"], "backupNo": filter["backupNo"]}})
                dict["status"] = "Data Updated Successfully !!"
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route('/zomatoentity')
@login_required
def zomatoentity():
    property_Restaurant = []
    try:
        property_Restaurant = list(
            app.config['PROPERTY_COLLECTION'].find(
                {"Status": "Active", "For": "Restaurant", "type": "Customer", "source": "Zomato"}))
    except Exception as e:
        print(e)
    return render_template('zomatoEntityId.html', property_Restaurant=property_Restaurant)


@app.route('/entityDetails', methods=["GET", "POST"])
@login_required
def entityDetails():
    al = app.config['ZOMATO_ENTITYID_COLLECTION'].find()
    return json.dumps({"entityDetails": json.loads(json_util.dumps(al))})


@app.route('/entityidSave', methods=["GET", "POST"])
@login_required
def entityidSave():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            try:
                app.config['ZOMATO_ENTITYID_COLLECTION'].update(
                    {"Name": filter['Name'], "Place": filter['Place'], "City": filter['City'], "State": filter['State'],
                     "Country": filter['Country']},
                    {"Name": filter['Name'], "Place": filter['Place'], "City": filter['City'], "State": filter['State'],
                     "Country": filter['Country'], "EntityId": filter['EntityId']}, upsert=True)
                print("Entity-Id Saved")
                status = "Success"
            except:
                print("Entity-Id is not Saved")
                status = "Error"
            return json.dumps({"response": status})
        else:
            print("Nothing to Add")
            return json.dumps({"response": "Error"})
    else:
        print("No Data Available")
        return json.dumps({"response": "Error"})


@app.route('/guest_fdb/thankyoumsg')
def thankyou():
    return render_template('thankyou.html')


# ---------- Admin Panel -------------
# -----Guest feedback ------
@app.route('/guest_fdb/<propertyname>')
def guest_feedbacks(propertyname):
    print(propertyname)
    count = app.config['PROPERTY_COLLECTION'].find({'propertyName': propertyname}).count()
    if count > 0:
        return render_template('guest_fdb.html')
    else:
        return abort(404)


@app.route('/guest_fdb/<propertyname>/get_form', methods=['POST'])
def guest_feedback_data(propertyname):
    if request.method == 'POST':
        data = request.get_json()
        data['propertyName'] = propertyname
        data['date'] = int(datetime.datetime.today().timestamp())
        result = app.config['GUEST_FEEDBACK'].insert(data)
        if type(result) == ObjectId:
            return json.dumps({'status': 'success'})
        else:
            return json.dumps({'status': 'success'})


@app.route('/guest_fdb_client/')
@login_required
def client_report_guest_fdb():
    return render_template('guestfdbdash.html')


@app.route('/guest_fdb_client/report', methods=['POST'])
@login_required
def guest_fdb_report():
    if request.method == 'POST':
        data = request.get_json()
        start = data['start_dt']
        end = data['end_dt']
        topic = data['topic']
        fdb_db = app.config['GUEST_FEEDBACK']
        no_reviews = fdb_db.find({'propertyName': session['user']['hotel']}).count()

        rating_dist = fdb_db.aggregate()
