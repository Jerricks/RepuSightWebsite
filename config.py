from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Put your secret key here'
DB_NAME = 'proDB'
DB_NAME_CRAWLER = 'crawlerDB'
#ip = '127.0.0.1'  # While project is running live, use this local IP
# ip = '13.126.57.117'
#ip = '35.154.116.6' # repupro instance public IP, while we want to connect from local to remote
ip = '52.66.167.52'
port = 27017
DATABASE = MongoClient(ip, port)[DB_NAME]
DATABASE_CRAWLER = MongoClient(ip, port)[DB_NAME_CRAWLER]

REGISTEREDUSERS_COLLECTION = DATABASE.registeredUsers
HOTEL_COLLECTION = DATABASE.hotelData
RESTAURANT_COLLECTION = DATABASE.restaurantData
SOCIALMEDIADATA_COLLECTION = DATABASE.socialMediaData
TICKET_COLLECTION = DATABASE.ticketData
REPLYCREDENTIALS_COLLECTION = DATABASE.replyLoginCredentials
ZOMATO_ENTITYID_COLLECTION = DATABASE.zmEntityId
DEPTHOTEL_COLLECTION = DATABASE.departmentHeadsHotel
DEPTRESTAURANT_COLLECTION = DATABASE.departmentHeadsRestaurant
SAVEDEMAILDATA_COLLECTION = DATABASE.savedEmailData
SMSDATA_COLLECTION = DATABASE.smsData
REPLIES_COLLECTION = DATABASE.replies

COUNTRY_COLLECTION = DATABASE_CRAWLER.countries
STATE_COLLECTION = DATABASE_CRAWLER.states
CITY_COLLECTION = DATABASE_CRAWLER.city
AREAS_COLLECTION = DATABASE_CRAWLER.area
SOURCES_COLLECTION = DATABASE_CRAWLER.sources
PROPERTY_COLLECTION = DATABASE_CRAWLER.properties
SEQUENCE_COLLECTION = DATABASE_CRAWLER.seqs
GUEST_FEEDBACK = DATABASE.guestFeedback

FB_TOKEN = "342093956136947|QD8JqM4FAjErakLAi6EtCkaquqE"
MSG_TOKEN = "131640AnPUovS0ZQU5832b5b2"

MAIL_SERVER = 'smtp.zoho.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'support@repusight.com'
MAIL_PASSWORD = 'repusight'
DEFAULT_MAIL_SENDER = 'support@repusight.com'



# mongoimport -d proDB -c hotelData --type csv --file /home/repusight/Desktop/chianti_classified.csv --headerline

# db.registeredUsers.update({"_id": "sarovar"}, {"$set": {"_id": "sarovar", "Logo": "/static/images/Sarovar_logo.jpg"}})

# db.socialMediaData.insert({"_id": "sarovar","hotel": "Davanam Sarovar Portico Suites", "Place": "Madivala", "fbkeyword": "davanamsarovar", "twitterkeyword": "SarovarDavanam", "instagramkeyword": "davanamsarovarpractosuites"})


# db.registeredUsers.update({"_id": "ammisbaner"}, {"$set": {"_id": "ammisbaner", "Logo": "/static/images/ammislogo1.png"}})
#
# db.socialMediaData.insert({"_id": "ammisbaner","hotel": "Ammi's Biryani, Bannerghatta", "Place": "Bannerghatta", "fbkeyword": "AmmisBiryani", "twitterkeyword": "ammisbiryani", "instagramkeyword": ""})

# { "_id" : "sarovar", "Place" : "Madivala", "hotel" : "Davanam Sarovar Portico Suites", "phone" : "8970645878", "propType" : "Hotel", "status" : "true", "password" : "pbkdf2:sha256:1000$c5bRZ44P$d24969e9ec15d1d9b5dce97000f735bc64f57253c2d1f784e470fa170803b5fa", "role" : "Manager", "username" : "sarovar", "email" : "managerabc@sarovar.com", "Logo" : "/static/images/Sarovar_logo.jpg", "group" : [ { "Name" : "DoubleTree Suites by Hilton", "Place" : "Sarjapur" }, { "Name" : "Holiday Inn & Suites", "Place" : "Whitefield" } ] }

# db.hotelData.update({"Logo": "/static/images/DAVANAM_bengaluru_logo_ltjvys.jpg"}, {"$set": {""Logo": "/static/images/Sarovar_logo.jpg"}})


# scp -i ~/Documents/repulink.pem ~/Desktop/master_ammis_all.csv  ubuntu@ec2-35-154-116-6.ap-south-1.compute.amazonaws.com:~/

# db.registeredUsers.update({"_id": "sarovar"}, {"$set": {"_id": "sarovar", "group": [ { "Name" : "Grand Mercure", "Place" : "Kormangala" }, { "Name" : "DoubleTree Suites by Hilton", "Place" : "Sarjapur" }, {"Name": "IBIS", "Place":"Hosur Road"}, {"Name": "Keys Hotel", "Place":"Hosur Road"}, { "Name" : "Lemon Tree", "Place" : "Electronics City" }, { "Name" : "Crowne Plaza", "Place" : "Electronic City" }, { "Name" : "The Chancery Pavilion", "Place" : "Residency Road" }, { "Name" : "Royal Orchid Central", "Place" : "Dickenson Road" }, { "Name" : "Ramada Encore", "Place" : "Domlur" }, { "Name" : "The Paul", "Place" : "Domlur" } ]}})

# db.hotelData.update({"Name": "Davanam Sarovar Portico Suites", "Channel": "Booking", "Replied": 0, "Comment": "There are no comments available for this review"}, {"$set": {"Replied": 1}}, { multi: true })

# db.hotelData.update({"Name": "Davanam Sarovar Portico Suites", "Channel": "MakeMyTrip", "Replied": ""}, {"$set": {"Replied": 2}}, { multi: true })
