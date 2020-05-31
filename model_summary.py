from app import app
from flask import session
import datetime as dtm
import time
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
}

topicHotel = ['Food', 'Service', 'Value', 'Ambience', 'Cleanliness', 'Amenities', 'Hospitality', 'Location',
              'Front-Desk', 'Room']

topicRestaurant = ['Taste', 'Variety', 'Drinks', 'Service', 'Value', 'Hygiene', 'Ambience', 'Hospitality', 'Comforts',
                   'Entertainment']


def check_collection():
    user_obj = session.get('user', None)
    if user_obj['propType'] == 'Hotel':
        connect = app.config['HOTEL_COLLECTION']
    elif user_obj['propType'] == 'Restaurant':
        connect = app.config['RESTAURANT_COLLECTION']
    return connect


def hotelDetails():
    user_obj = session.get('user', None)
    city_all = user_obj['City']
    data = []
    if city_all == "True":
        data.append({"Name": user_obj['hotel'], "City": user_obj['City_Name'], "Logo": user_obj['Logo']})
    else:
        data.append({"Name": user_obj['hotel'], "Place": user_obj['Place'], "Logo": user_obj['Logo']})
    return data


def getPlaceList():
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    data = []
    collection = check_collection()
    distinctPlace = collection.find({"Name": name}).distinct("Place")
    if name in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]:
        distinctPlace.insert(0, "-- All --")
    for place in distinctPlace:
        data.append({"keyplace": place, "valueplace": place})
    return data


def getReviewCount(name, place, sentiment, startDate, endDate, city):
    collection = check_collection()
    if city is None:
        if startDate == None and endDate == None:
            if sentiment != None:
                reviewCount = collection.find({'Name': name, 'Place': place, 'Sentiment': sentiment}).count()
            else:
                reviewCount = collection.find({'Name': name, 'Place': place, 'Sentiment': {'$ne': 3}}).count()
        else:
            if sentiment != None:
                reviewCount = collection.find({'Name': name, 'Place': place, 'Sentiment': sentiment,
                                               'Date': {'$gte': startDate, '$lt': endDate}}).count()
            else:
                reviewCount = collection.find(
                    {'Name': name, 'Place': place, 'Sentiment': {'$ne': 3},
                     'Date': {'$gte': startDate, '$lt': endDate}}).count()
    else:
        if startDate == None and endDate == None:
            if sentiment != None:
                reviewCount = collection.find({'Name': name, 'City': city, 'Sentiment': sentiment}).count()
            else:
                reviewCount = collection.find({'Name': name, 'City': city, 'Sentiment': {'$ne': 3}}).count()
        else:
            if sentiment != None:
                reviewCount = collection.find({'Name': name, 'City': city, 'Sentiment': sentiment,
                                               'Date': {'$gte': startDate, '$lt': endDate}}).count()
            else:
                reviewCount = collection.find(
                    {'Name': name, 'City': city, 'Sentiment': {'$ne': 3},
                     'Date': {'$gte': startDate, '$lt': endDate}}).count()
    return reviewCount


def last7Days(place, collection):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    sevendays = dtm.date.today() - dtm.timedelta(7)
    unix_time_7days = int(sevendays.strftime("%s"))
    unix_time_today = int(dtm.date.today().strftime("%s"))
    data = []
    if place == "-- All --":
        total_reviews = collection.find(
            {'Name': name, 'City': city, 'Sentiment': {'$ne': 3},
             'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
        postive_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 1,
                                           'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
        negative_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 2,
                                            'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
        neutral_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 0,
                                           'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
    else:
        total_reviews = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Sentiment': {'$ne': 3},
             'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
        postive_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 1,
                                           'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
        negative_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 2,
                                            'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
        neutral_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 0,
                                           'Date': {'$gte': unix_time_7days, '$lt': unix_time_today}}).count()
    if total_reviews == 0:
        CSI = 0
    else:
        CSI = total_reviews * 2 - (neutral_reviews * 0.5) - negative_reviews
        CSI /= total_reviews * 2
        CSI *= 100.0
    data.append({"CSI": round(CSI, 2), "total_reviews": total_reviews,
                 "positive_reviews": postive_reviews, "negative_reviews": negative_reviews})
    return data


def presentMonth(place, collection):
    dt = dtm.datetime(year=int(time.strftime("%Y")), month=int(time.strftime("%m")), day=1)
    unix_time_month_first = int(time.mktime(dt.timetuple()))
    unix_time_today = int(dtm.date.today().strftime("%s"))
    data = []
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    if place == "-- All --":
        total_reviews = collection.find(
            {'Name': name, 'City': city, 'Sentiment': {'$ne': 3},
             'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
        postive_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 1,
                                           'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
        negative_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 2,
                                            'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
        neutral_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 0,
                                           'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
    else:
        total_reviews = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Sentiment': {'$ne': 3},
             'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
        postive_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 1,
                                           'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
        negative_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 2,
                                            'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
        neutral_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 0,
                                           'Date': {'$gte': unix_time_month_first, '$lt': unix_time_today}}).count()
    if total_reviews == 0:
        CSI = 0
    else:
        CSI = total_reviews * 2 - (neutral_reviews * 0.5) - negative_reviews
        CSI /= total_reviews * 2
        CSI *= 100.0
    data.append({"CSI": round(CSI, 2), "total_reviews": total_reviews, "positive_reviews": postive_reviews,
                 "negative_reviews": negative_reviews})
    return data


def lastMonth(place, collection):
    dt = dtm.datetime(year=int(time.strftime("%Y")), month=int(time.strftime("%m")), day=1)
    unix_time_month_first = int(time.mktime(dt.timetuple()))
    dt = dtm.datetime(year=int(time.strftime("%Y")), month=int(time.strftime("%m")), day=1) - dtm.timedelta(31)
    unix_time_last_month_first = int(time.mktime(dt.timetuple()))
    data = []
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    if place == "-- All --":
        total_reviews = collection.find(
            {'Name': name, 'City': city, 'Sentiment': {'$ne': 3},
             'Date': {'$gte': unix_time_last_month_first, '$lt': unix_time_month_first}}).count()
        postive_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 1,
                                           'Date': {'$gte': unix_time_last_month_first,
                                                    '$lt': unix_time_month_first}}).count()
        negative_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 2,
                                            'Date': {'$gte': unix_time_last_month_first,
                                                     '$lt': unix_time_month_first}}).count()
        neutral_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': 0,
                                           'Date': {'$gte': unix_time_last_month_first,
                                                    '$lt': unix_time_month_first}}).count()
    else:
        total_reviews = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Sentiment': {'$ne': 3},
             'Date': {'$gte': unix_time_last_month_first, '$lt': unix_time_month_first}}).count()
        postive_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 1,
                                           'Date': {'$gte': unix_time_last_month_first,
                                                    '$lt': unix_time_month_first}}).count()
        negative_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 2,
                                            'Date': {'$gte': unix_time_last_month_first,
                                                     '$lt': unix_time_month_first}}).count()
        neutral_reviews = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 0,
                                           'Date': {'$gte': unix_time_last_month_first,
                                                    '$lt': unix_time_month_first}}).count()
    if total_reviews == 0:
        CSI = 0
    else:
        CSI = total_reviews * 2 - (neutral_reviews * 0.5) - negative_reviews
        CSI /= total_reviews * 2
        CSI *= 100.0
    data.append({"CSI": round(CSI, 2), "total_reviews": total_reviews, "positive_reviews": postive_reviews,
                 "negative_reviews": negative_reviews})
    return data


def totalReviews(place, collection):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    data = []
    city_all = user_obj['City']
    if place == "-- All --":
        if city_all == "True":
            total_reviews = collection.find({'Name': name, 'City': city}).count()
        else:
            total_reviews = collection.find({'Name': name, 'Place': place}).count()
        total_reviews_pos = getReviewCount(name, place, 1, None, None, city)
        total_reviews_Neg = getReviewCount(name, place, 2, None, None, city)
    else:
        if city_all == "True":
            total_reviews = collection.find({'Name': name, 'Place': place, 'City': city}).count()
        else:
            total_reviews = collection.find({'Name': name, 'Place': place}).count()
        total_reviews_pos = getReviewCount(name, place, 1, None, None, city)
        total_reviews_Neg = getReviewCount(name, place, 2, None, None, city)
    data.append({"total_reviews": total_reviews, "positive_reviews": total_reviews_pos,
                 "negative_reviews": total_reviews_Neg})
    return data


def avgRating(place, collection):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    if place == "-- All --":
        if city_all == "True":
            data = list(collection.aggregate([{"$match": {"Name": name, "City": city}},
                                              {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
        else:
            data = list(collection.aggregate([{"$match": {"Name": name, "Place": place}},
                                              {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
    else:
        if city_all == "True":
            data = list(collection.aggregate([{"$match": {"Name": name, "Place": place, "City": city}},
                                              {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
        else:
            data = list(collection.aggregate([{"$match": {"Name": name, "Place": place}},
                                              {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
    data = round(data[0]['avg_rating'], 2)
    return data


def ranking():
    collection = check_collection()
    user_obj = session.get('user', None)
    # city = user_obj['City_Name']
    # tags = collection.distinct("Name")
    # place = collection.distinct("Place")
    city_all = user_obj['City']
    if city_all == "True":
        al = list(collection.aggregate(
            [{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "Logo": "$Logo", "City": "$City"}}}]))
        al1 = list(collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Logo": "$Logo", "City": "$City"}}}]))
        data = []
        data1 = []
        data2 = []
        for ele in al1:
            name = ele["_id"]["Name"]
            city = ele["_id"]["City"]
            total_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': {'$ne': 3}}).count()
            total_reviews_pos = collection.find({'Name': name, 'City': city, 'Sentiment': 1}).count()
            total_reviews_Neg = collection.find({'Name': name, 'City': city, 'Sentiment': 2}).count()
            total_reviews_Neu = collection.find({'Name': name, 'City': city, 'Sentiment': 0}).count()
            if total_reviews != 0:
                CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
                CSI /= 2 * total_reviews
            else:
                CSI = 0
            data2.append({'Hotel': name, 'City': city, 'CSI': round(CSI, 2), 'Logo': ele["_id"]["Logo"]})
        newlist1 = sorted(data2, key=lambda k: k['CSI'], reverse=True)
        for ele in al:
            name = ele["_id"]["Name"]
            place = ele["_id"]["Place"]
            city = ele["_id"]["City"]
            total_reviews = getReviewCount(name, place, None, None, None, None)
            total_reviews_pos = getReviewCount(name, place, 1, None, None, None)
            total_reviews_Neg = getReviewCount(name, place, 2, None, None, None)
            total_reviews_Neu = getReviewCount(name, place, 0, None, None, None)
            if total_reviews != 0:
                CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
                CSI /= 2 * total_reviews
            else:
                CSI = 0
            data.append({'Hotel': name, 'Place': place, 'City': city, 'CSI': round(CSI, 2), 'Logo': ele["_id"]["Logo"]})
        newlist = sorted(data, key=lambda k: k['CSI'], reverse=True)
        rankset = []
        s = set()
        for i in newlist1:
            s.add(i['CSI'])
        rankset = sorted(s, reverse=True)
        user_obj = session.get('user', None)
        name1 = user_obj['hotel']
        place1 = user_obj['Place']
        city1 = user_obj['City']
        count = 0
        for ele in newlist1:
            # if ele['Hotel'] == name1 and ele['City'] == city1:
            if ele['Hotel'] == name1:
                # rank = count + 1
                for r in rankset:
                    if r == ele['CSI']:
                        rank = rankset.index(r) + 1
                        break
            else:
                count = count + 1
                # rank = newlist.index(ele) + 1
        data1.append({"rank": rank, "total": len(al1), "newlist": newlist})
    else:
        if user_obj['propType'] == "Restaurant":
            al = list(
                collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "Logo": "$Logo"}}}]))
            data = []
            data1 = []
            gen = list(
                (ele for ele in al if ele["_id"]["Name"] not in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]))
            for ele in gen:
                name = ele["_id"]["Name"]
                place = ele["_id"]["Place"]
                total_reviews = getReviewCount(name, place, None, None, None, None)
                total_reviews_pos = getReviewCount(name, place, 1, None, None, None)
                total_reviews_Neg = getReviewCount(name, place, 2, None, None, None)
                total_reviews_Neu = getReviewCount(name, place, 0, None, None, None)
                if total_reviews != 0:
                    CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
                    CSI /= 2 * total_reviews
                else:
                    CSI = 0
                data.append({'Hotel': name, 'Place': place, 'CSI': round(CSI, 2), 'Logo': ele["_id"]["Logo"]})
            al1 = list(collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Logo": "$Logo", "City": "$City"}}}]))
            gen1 = list(
                (ele for ele in al1 if ele["_id"]["Name"] in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]))
            for ele in gen1:
                name = ele["_id"]["Name"]
                city = ele["_id"]["City"]
                total_reviews = collection.find({'Name': name, 'City': city, 'Sentiment': {'$ne': 3}}).count()
                total_reviews_pos = collection.find({'Name': name, 'City': city, 'Sentiment': 1}).count()
                total_reviews_Neg = collection.find({'Name': name, 'City': city, 'Sentiment': 2}).count()
                total_reviews_Neu = collection.find({'Name': name, 'City': city, 'Sentiment': 0}).count()
                if total_reviews != 0:
                    CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
                    CSI /= 2 * total_reviews
                else:
                    CSI = 0
                data.append({'Hotel': name, 'Place': city, 'CSI': round(CSI, 2), 'Logo': ele["_id"]["Logo"]})
            newlist = sorted(data, key=lambda k: k['CSI'], reverse=True)
            rankset = []
            s = set()
            for i in newlist:
                s.add(i['CSI'])
            rankset = sorted(s, reverse=True)
            user_obj = session.get('user', None)
            name1 = user_obj['hotel']
            place1 = user_obj['Place']
            count = 0
            for ele in newlist:
                if ele['Hotel'] == name1 and ele['Place'] == place1:
                    for r in rankset:
                        if r == ele['CSI']:
                            rank = rankset.index(r) + 1
                            # rank = count + 1
                            # rank = rankset.index(r) for r in rankset if r == ele['CSI']
                            break
                else:
                    count = count + 1
            # data1.append({"rank": rank, "total": (len(gen)+len(al1)), "newlist":newlist})
            data1.append({"rank": rank, "total": len(newlist), "newlist": newlist})
        if user_obj['propType'] == "Hotel":
            al = list(
                collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "Logo": "$Logo"}}}]))
            data = []
            data1 = []
            for ele in al:
                name = ele["_id"]["Name"]
                place = ele["_id"]["Place"]
                total_reviews = getReviewCount(name, place, None, None, None, None)
                total_reviews_pos = getReviewCount(name, place, 1, None, None, None)
                total_reviews_Neg = getReviewCount(name, place, 2, None, None, None)
                total_reviews_Neu = getReviewCount(name, place, 0, None, None, None)
                if total_reviews != 0:
                    CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
                    CSI /= 2 * total_reviews
                else:
                    CSI = 0
                data.append({'Hotel': name, 'Place': place, 'CSI': round(CSI, 2), 'Logo': ele["_id"]["Logo"]})
            newlist = sorted(data, key=lambda k: k['CSI'], reverse=True)
            rankset = []
            s = set()
            for i in newlist:
                s.add(i['CSI'])
            rankset = sorted(s, reverse=True)
            user_obj = session.get('user', None)
            name1 = user_obj['hotel']
            place1 = user_obj['Place']
            count = 0
            for ele in newlist:
                if ele['Hotel'] == name1 and ele['Place'] == place1:
                    for r in rankset:
                        if r == ele['CSI']:
                            rank = rankset.index(r) + 1
                            # rank = count + 1
                            # rank = rankset.index(r) for r in rankset if r == ele['CSI']
                            break
                else:
                    count = count + 1
            data1.append({"rank": rank, "total": len(al), "newlist": newlist})
    return data1


def summaryOTA(place, collection):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    data = []
    if city_all == "True" and place == "-- All --":
        al = list(collection.aggregate(
            [{"$match": {"Name": name, "City": city}},
             {"$group": {"_id": {"Name": name, "City": city, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            total_reviews = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"]}).count()
            avg_rating_list = list(collection.aggregate(
                [{"$match": {"Name": name, "City": city, "Channel": ele["_id"]["Channel"]}},
                 {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
            if avg_rating_list != []:
                avg_rating = round(avg_rating_list[0]['avg_rating'], 2)
            else:
                avg_rating = 0
            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"], "total_reviews": total_reviews,
                         "avg_rating": avg_rating})
    else:
        al = list(collection.aggregate([{"$match": {"Name": name, "Place": place}}, {
            "$group": {"_id": {"Name": name, "Place": place, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            total_reviews = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"]}).count()
            avg_rating_list = list(collection.aggregate(
                [{"$match": {"Name": name, "Place": place, "Channel": ele["_id"]["Channel"]}},
                 {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
            if avg_rating_list != []:
                avg_rating = round(avg_rating_list[0]['avg_rating'], 2)
            else:
                avg_rating = 0
            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"], "total_reviews": total_reviews,
                         "avg_rating": avg_rating})
    newdata = sorted(data, key=lambda k: k['avg_rating'], reverse=True)
    return newdata


def summaryCA():
    collection = check_collection()
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    group = user_obj['group']
    if group != []:
        group.insert(0, {"Name": name, "Place": place})
    else:
        if name != "Ammi's Biryani" and name != "RICE BAR" and name != "Sultan's Biryani":
            group.insert(0, {"Name": name, "Place": place})
        else:
            al = list(
                collection.aggregate(
                    [{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "City": "$City", "_id": "$_id"}}}]))
            for i in al:
                nname = i["_id"]["Name"]
                if nname == name:
                    nplace = i["_id"]["Place"]
                    group.insert(0, {"Name": nname, "Place": nplace})
    city_all = user_obj['City']
    city = user_obj['City_Name']
    func_ranking = ranking()
    newlist = func_ranking[0]['newlist']
    data = []
    rankset = []
    s = set()
    for i in newlist:
        s.add(i['CSI'])
    rankset = sorted(s, reverse=True)
    count = 0
    for hotel in group:
        hname = hotel["Name"]
        hplace = hotel["Place"]
        for ele in newlist:
            if ele['Hotel'] == hname and ele['Place'] == hplace:
                for r in rankset:
                    if r == ele['CSI']:
                        rank = rankset.index(r) + 1
                        break
                    else:
                        count = count + 1
                if name != "Ammi's Biryani" and name != "RICE BAR" and name != "Sultan's Biryani":
                    data.append({"rank": rank, 'Hotel': ele['Hotel'], 'Place': ele['Place'], 'CSI': ele['CSI'],
                                 'Logo': ele['Logo']})
                else:
                    if ele['Hotel'] == "Ammi's Biryani" or ele['Hotel'] == "RICE BAR" or ele['Hotel'] == "Sultan's Biryani":
                        data.append({"rank": rank, 'Hotel': ele['Hotel'], 'Place': ele['Place'], 'CSI': ele['CSI'],
                                     'Logo': ele['Logo']})
                    else:
                        continue

    return data


def yeardropdown(place, collection):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    data1 = []
    if place == "-- All --":
        data = list(collection.distinct("Date", {"Name": name, "City": city}))
    else:
        data = list(collection.distinct("Date", {"Name": name, "Place": place, "City": city}))
    for d in data:
        data1.append(dtm.datetime.fromtimestamp(int(d)).strftime('%Y'))
    data1 = sorted(list(set(data1)))
    return data1


def summaryChart(place, collection, year):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    city_all = user_obj['City']
    data = []
    enddate = int(dtm.datetime(year=int(year), month=12, day=31).strftime("%s"))
    startdate = int(dtm.datetime(year=int(year), month=1, day=1).strftime("%s"))
    columns = ['year', 'month', 'sentiment']
    lis = list()
    m_all = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if place == "-- All --" and city_all == "True":
        total_reviews = collection.find({'Name': name, 'City': city, 'Date': {'$gte': startdate, '$lt': enddate}})
    else:
        total_reviews = collection.find({'Name': name, 'Place': place, 'Date': {'$gte': startdate, '$lt': enddate}})
    for x in total_reviews:
        lis.append([dtm.datetime.fromtimestamp(int(x['Date'])).strftime('%Y'),
                           dtm.datetime.fromtimestamp(int(x['Date'])).strftime('%m'),
                           str(x['Sentiment'])])
#        df.loc[len(df)] = [dtm.datetime.fromtimestamp(int(x['Date'])).strftime('%Y'),
#                           dtm.datetime.fromtimestamp(int(x['Date'])).strftime('%m'),
#                           str(x['Sentiment'])]
    df = pd.DataFrame(lis,columns=columns)
    df_sentiment = pd.get_dummies(df['sentiment'])
    df_new = pd.concat([df, df_sentiment], axis=1)
    df = df_new.groupby(['year', 'month']).sum().reset_index()
    if "2" not in list(df):
        df['2'] = 0.0
    if "1" not in list(df):
        df['1'] = 0.0
    if "0" not in list(df):
        df['0'] = 0.0
    if "3" not in list(df):
        df['3'] = 0.0
    data_csi = []
    data_review = []
    month_list = []
    for index, row in df.iterrows():
        total = row['1'] + row['0'] + row['2']
        if total == 0:
            CSI = 0
        else:
            CSI = total * 2 - (row['0'] * 0.5) - row['2']
            CSI /= total * 2
            CSI *= 100.0
        reviewsNum = row['1'] + row['0'] + row['2'] + row['3']
        month = dtm.datetime.strptime(row['month'], '%m').strftime("%b")
        month_list.append(month)
        data_csi.append([month, round(CSI, 2)])
        data_review.append([month, int(reviewsNum)])
    for m in m_all:
        if m not in month_list:
            data_csi.append([m, 0])
            data_review.append([m, 0])
    data_csi_final = sorted(data_csi, key=lambda x: m_all.index(x[0]))
    data_review_final = sorted(data_review, key=lambda x: m_all.index(x[0]))
    data.append({"data_csi": data_csi_final, "data_review": data_review_final})
    return data


def deptIndex(place, collection, start, end):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    city = user_obj['City_Name']
    city_all = user_obj['City']
    data = []
    if user_obj['propType'] == 'Hotel':
        TopicCategories = topicHotel
    elif user_obj['propType'] == 'Restaurant':
        TopicCategories = topicRestaurant
    if city_all == "True" and place == "-- All --":
        for x in TopicCategories:
            total_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                           'Date': {'$gte': start, '$lt': end},
                                                           x: {'$ne': 3}}).count()
            postive_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 1}).count()
            negative_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                              'Date': {'$gte': start, '$lt': end},
                                                              x: 2}).count()
            neutral_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 0}).count()
            if total_reviews_present_month == 0:
                CSI_present_month = 0
            else:
                CSI_present_month = (
                                        2 * total_reviews_present_month - (
                                        neutral_reviews_present_month * 0.5) - negative_reviews_present_month) * 100.0
                CSI_present_month /= 2 * total_reviews_present_month

            total_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                        'Date': {'$gte': 2 * start - end, '$lt': start},
                                                        x: {'$ne': 3}}).count()
            postive_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                          'Date': {'$gte': 2 * start - end,
                                                                   '$lt': start}, x: 1}).count()
            negative_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                           'Date': {'$gte': 2 * start - end,
                                                                    '$lt': start}, x: 2}).count()
            neutral_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                          'Date': {'$gte': 2 * start - end,
                                                                   '$lt': start}, x: 0}).count()

            if total_reviews_last_month == 0:
                CSI_last_month = 0
            else:
                CSI_last_month = (2 * total_reviews_last_month - (
                    neutral_reviews_last_month * 0.5) - negative_reviews_last_month) * 100.0
                CSI_last_month /= 2 * total_reviews_last_month
            if CSI_last_month != 0.0:
                change = (CSI_present_month - CSI_last_month) * 100.0
                change /= CSI_last_month
            else:
                change = 100.0
            if change < 0:
                change = -(change)
                csiUpDown = "fa-caret-down"
                csiClass = "text-red"
            elif change == 0 or change > 0:
                csiUpDown = "fa-caret-up"
                csiClass = "text-green"
            data.append({"topic": x, "CSI": round(CSI_present_month, 2), "CSIchange": round(change, 2),
                         "csiUpDown": csiUpDown, "csiClass": csiClass,
                         "mention": total_reviews_present_month, "positive": postive_reviews_present_month,
                         "Negative": negative_reviews_present_month,
                         "Neutral": neutral_reviews_present_month})
    else:
        for x in TopicCategories:
            total_reviews_present_month = collection.find({'Name': name, 'Place': place,
                                                           'Date': {'$gte': start, '$lt': end},
                                                           x: {'$ne': 3}}).count()
            postive_reviews_present_month = collection.find({'Name': name, 'Place': place,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 1}).count()
            negative_reviews_present_month = collection.find({'Name': name, 'Place': place,
                                                              'Date': {'$gte': start, '$lt': end},
                                                              x: 2}).count()
            neutral_reviews_present_month = collection.find({'Name': name, 'Place': place,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 0}).count()
            if total_reviews_present_month == 0:
                CSI_present_month = 0
            else:
                CSI_present_month = (
                                        2 * total_reviews_present_month - (
                                        neutral_reviews_present_month * 0.5) - negative_reviews_present_month) * 100.0
                CSI_present_month /= 2 * total_reviews_present_month

            total_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                        'Date': {'$gte': 2 * start - end, '$lt': start},
                                                        x: {'$ne': 3}}).count()
            postive_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                          'Date': {'$gte': 2 * start - end,
                                                                   '$lt': start}, x: 1}).count()
            negative_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                           'Date': {'$gte': 2 * start - end,
                                                                    '$lt': start}, x: 2}).count()
            neutral_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                          'Date': {'$gte': 2 * start - end,
                                                                   '$lt': start}, x: 0}).count()

            if total_reviews_last_month == 0:
                CSI_last_month = 0
            else:
                CSI_last_month = (2 * total_reviews_last_month - (
                    neutral_reviews_last_month * 0.5) - negative_reviews_last_month) * 100.0
                CSI_last_month /= 2 * total_reviews_last_month
            if CSI_last_month != 0.0:
                change = (CSI_present_month - CSI_last_month) * 100.0
                change /= CSI_last_month
            else:
                change = 100.0
            if change < 0:
                change = -(change)
                csiUpDown = "fa-caret-down"
                csiClass = "text-red"
            elif change == 0 or change > 0:
                csiUpDown = "fa-caret-up"
                csiClass = "text-green"
            data.append({"topic": x, "CSI": round(CSI_present_month, 2), "CSIchange": round(change, 2),
                         "csiUpDown": csiUpDown, "csiClass": csiClass,
                         "mention": total_reviews_present_month, "positive": postive_reviews_present_month,
                         "Negative": negative_reviews_present_month,
                         "Neutral": neutral_reviews_present_month})
    return data


def getSummaryData(place, year, startdate, enddate):
    t1 = time.time()
    collection = check_collection()
    sevenDayScore = last7Days(place=place, collection=collection)
    presentMonthScore = presentMonth(place=place, collection=collection)
    lastMonthScore = lastMonth(place=place, collection=collection)
    totalRev = totalReviews(place=place, collection=collection)
    averageRating = avgRating(place=place, collection=collection)
    sumOTA = summaryOTA(place=place, collection=collection)
    rank = ranking()
    yeardd = yeardropdown(place=place, collection=collection)
    chartdata = summaryChart(place=place, collection=collection, year=year)
    deptindexdata = deptIndex(place=place, collection=collection, start=startdate, end=enddate)
    dict = {"sevenDayScore": sevenDayScore, "presentMonthScore": presentMonthScore, "lastMonthScore": lastMonthScore,
            "totalRev": totalRev, "averageRating": averageRating, "rank": rank, "sumOTA": sumOTA, "yeardd": yeardd,
            "chartdata": chartdata, "deptindexdata": deptindexdata}
    t2 = time.time()
    print(t2 - t1)
    return dict
