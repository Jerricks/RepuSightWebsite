from app import app
from flask import session
from .model_summary import check_collection

topicHotel = [{"topicName": "Food", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Service", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Value", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Ambience", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Cleanliness", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Amenities", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Hospitality", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Location", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Front-Desk", "topicColor": "progress-bar-skyblue"},
              {"topicName": "Room", "topicColor": "progress-bar-skyblue"}]

topicRestaurant = [{"topicName": "Taste", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Variety", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Drinks", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Service", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Value", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Hygiene", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Ambience", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Hospitality", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Comforts", "topicColor": "progress-bar-skyblue"},
                   {"topicName": "Entertainment", "topicColor": "progress-bar-skyblue"}]


def allSourceData():
    collection = check_collection()
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    data = []
    if city_all == "True":
        al = list(collection.aggregate(
            [{"$match": {"Name": name, "City": city}},
             {"$group": {"_id": {"Name": name, "City": city, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            avg_rating_list = list(collection.aggregate(
                [{"$match": {"Name": name, "City": city, "Channel": ele["_id"]["Channel"]}},
                 {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
            avg_rating = round(avg_rating_list[0]['avg_rating'], 2)
            total_reviews = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"]}).count()
            postive_reviews = collection.find(
                {'Name': name, 'City': city, 'Sentiment': 1, "Channel": ele["_id"]["Channel"]}).count()
            negative_reviews = collection.find(
                {'Name': name, 'City': city, 'Sentiment': 2, "Channel": ele["_id"]["Channel"]}).count()
            neutral_reviews = collection.find(
                {'Name': name, 'City': city, 'Sentiment': 0, "Channel": ele["_id"]["Channel"]}).count()
            if total_reviews == 0:
                CSI = 0
            else:
                CSI = total_reviews * 2 - (neutral_reviews * 0.5) - negative_reviews
                CSI /= total_reviews * 2
                CSI *= 100.0

            data_rating = []
            rating_total = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"]}).count()
            if rating_total != 0:
                rating_5 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 4, '$lte': 5}}).count()
                data_rating.append(
                    {'ratingType': 'Excellent', 'ratingReviews': rating_5, "progressBar": 'progress-bar-success',
                     'valueWidth': round((rating_5 / rating_total) * 100, 2)})
                rating_4 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 3, '$lte': 4}}).count()
                data_rating.append(
                    {'ratingType': 'Very Good', 'ratingReviews': rating_4, "progressBar": 'progress-bar-success',
                     'valueWidth': round((rating_4 / rating_total) * 100, 2)})
                rating_3 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 2, '$lte': 3}}).count()
                data_rating.append(
                    {'ratingType': 'Average', 'ratingReviews': rating_3, "progressBar": 'progress-bar-average',
                     'valueWidth': round((rating_3 / rating_total) * 100, 2)})
                rating_2 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 1, '$lte': 2}}).count()
                data_rating.append(
                    {'ratingType': 'Poor', 'ratingReviews': rating_2, "progressBar": 'progress-bar-warning',
                     'valueWidth': round((rating_2 / rating_total) * 100, 2)})
                rating_1 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 0, '$lte': 1}}).count()
                data_rating.append(
                    {'ratingType': 'Terrible', 'ratingReviews': rating_1, "progressBar": 'progress-bar-Terrible',
                     'valueWidth': round((rating_1 / rating_total) * 100, 2)})
            else:
                rating_5 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 4, '$lte': 5}}).count()
                data_rating.append(
                    {'ratingType': 'Excellent', 'ratingReviews': rating_5, "progressBar": 'progress-bar-success',
                     'valueWidth': 0})
                rating_4 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 3, '$lte': 4}}).count()
                data_rating.append(
                    {'ratingType': 'Very Good', 'ratingReviews': rating_4, "progressBar": 'progress-bar-success',
                     'valueWidth': 0})
                rating_3 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 2, '$lte': 3}}).count()
                data_rating.append(
                    {'ratingType': 'Average', 'ratingReviews': rating_3, "progressBar": 'progress-bar-average',
                     'valueWidth': 0})
                rating_2 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 1, '$lte': 2}}).count()
                data_rating.append(
                    {'ratingType': 'Poor', 'ratingReviews': rating_2, "progressBar": 'progress-bar-warning',
                     'valueWidth': 0})
                rating_1 = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 0, '$lte': 1}}).count()
                data_rating.append(
                    {'ratingType': 'Terrible', 'ratingReviews': rating_1, "progressBar": 'progress-bar-Terrible',
                     'valueWidth': 0})

            data_topic = []
            if user_obj['propType'] == 'Hotel':
                topics = topicHotel
            elif user_obj['propType'] == 'Restaurant':
                topics = topicRestaurant
            for x in topics:
                total_reviews_topic = collection.find({'Name': name, 'City': city,
                                                       "Channel": ele["_id"]["Channel"],
                                                       x['topicName']: {'$ne': 3}}).count()
                postive_reviews_topic = collection.find({'Name': name, 'City': city,
                                                         "Channel": ele["_id"]["Channel"],
                                                         x['topicName']: 1}).count()
                negative_reviews_topic = collection.find({'Name': name, 'City': city,
                                                          "Channel": ele["_id"]["Channel"],
                                                          x['topicName']: 2}).count()
                neutral_reviews_topic = collection.find({'Name': name, 'City': city,
                                                         "Channel": ele["_id"]["Channel"],
                                                         x['topicName']: 0}).count()
                if total_reviews_topic == 0:
                    CSI_topic = 0
                else:
                    CSI_topic = total_reviews_topic * 2 - (neutral_reviews_topic * 0.5) - negative_reviews_topic
                    CSI_topic /= total_reviews_topic * 2
                    CSI_topic *= 100.0
                data_topic.append(
                    {"topic": x['topicName'], "CSI_topic": round(CSI_topic, 2), "topicColor": x['topicColor']})

            repliednone = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R"}).count()
            repliednone1 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": ""}).count()
            replied0 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R0"}).count()
            replied1 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R1"}).count()
            replied2 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R2"}).count()

            if total_reviews == (repliednone + replied2 + repliednone1):
                mgtrespstr = "No"
            else:
                if total_reviews != 0:
                    mgtresp = round((replied1 / total_reviews) * 100, 2)
                    mgtrespstr = str(mgtresp) + "%"

            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"], "total_reviews": total_reviews,
                         "avg_rating": avg_rating, 'recommendation': round(avg_rating * 20, 2), "CSI": round(CSI, 2),
                         "pos_review": postive_reviews, "neu_review": neutral_reviews, "neg_review": negative_reviews,
                         "data_topic": data_topic, "data_rating": data_rating, "MgtResponse": mgtrespstr})
    else:
        al = list(collection.aggregate(
            [{"$match": {"Name": name, "Place": place}},
             {"$group": {"_id": {"Name": name, "Place": place, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            avg_rating_list = list(collection.aggregate(
                [{"$match": {"Name": name, "Place": place, "Channel": ele["_id"]["Channel"]}},
                 {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
            if avg_rating_list != []:
                avg_rating = round(avg_rating_list[0]['avg_rating'], 2)
            else:
                avg_rating = 0
            total_reviews = collection.find(
                {'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"]}).count()
            postive_reviews = collection.find(
                {'Name': name, 'Place': place, 'Sentiment': 1, "Channel": ele["_id"]["Channel"]}).count()
            negative_reviews = collection.find(
                {'Name': name, 'Place': place, 'Sentiment': 2, "Channel": ele["_id"]["Channel"]}).count()
            neutral_reviews = collection.find(
                {'Name': name, 'Place': place, 'Sentiment': 0, "Channel": ele["_id"]["Channel"]}).count()
            if total_reviews == 0:
                CSI = 0
            else:
                CSI = total_reviews * 2 - (neutral_reviews * 0.5) - negative_reviews
                CSI /= total_reviews * 2
                CSI *= 100.0

            data_rating = []
            rating_total = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"]}).count()
            if rating_total != 0:
                rating_5 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 4, '$lte': 5}}).count()
                data_rating.append(
                    {'ratingType': 'Excellent', 'ratingReviews': rating_5, "progressBar": 'progress-bar-success',
                     'valueWidth': round((rating_5 / rating_total) * 100, 2)})
                rating_4 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 3, '$lte': 4}}).count()
                data_rating.append(
                    {'ratingType': 'Very Good', 'ratingReviews': rating_4, "progressBar": 'progress-bar-success',
                     'valueWidth': round((rating_4 / rating_total) * 100, 2)})
                rating_3 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 2, '$lte': 3}}).count()
                data_rating.append(
                    {'ratingType': 'Average', 'ratingReviews': rating_3, "progressBar": 'progress-bar-average',
                     'valueWidth': round((rating_3 / rating_total) * 100, 2)})
                rating_2 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 1, '$lte': 2}}).count()
                data_rating.append(
                    {'ratingType': 'Poor', 'ratingReviews': rating_2, "progressBar": 'progress-bar-warning',
                     'valueWidth': round((rating_2 / rating_total) * 100, 2)})
                rating_1 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 0, '$lte': 1}}).count()
                data_rating.append(
                    {'ratingType': 'Terrible', 'ratingReviews': rating_1, "progressBar": 'progress-bar-Terrible',
                     'valueWidth': round((rating_1 / rating_total) * 100, 2)})
            else:
                rating_5 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 4, '$lte': 5}}).count()
                data_rating.append(
                    {'ratingType': 'Excellent', 'ratingReviews': rating_5, "progressBar": 'progress-bar-success',
                     'valueWidth': 0})
                rating_4 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 3, '$lte': 4}}).count()
                data_rating.append(
                    {'ratingType': 'Very Good', 'ratingReviews': rating_4, "progressBar": 'progress-bar-success',
                     'valueWidth': 0})
                rating_3 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 2, '$lte': 3}}).count()
                data_rating.append(
                    {'ratingType': 'Average', 'ratingReviews': rating_3, "progressBar": 'progress-bar-average',
                     'valueWidth': 0})
                rating_2 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 1, '$lte': 2}}).count()
                data_rating.append(
                    {'ratingType': 'Poor', 'ratingReviews': rating_2, "progressBar": 'progress-bar-warning',
                     'valueWidth': 0})
                rating_1 = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                            'Rating': {'$gt': 0, '$lte': 1}}).count()
                data_rating.append(
                    {'ratingType': 'Terrible', 'ratingReviews': rating_1, "progressBar": 'progress-bar-Terrible',
                     'valueWidth': 0})

            data_topic = []
            if user_obj['propType'] == 'Hotel':
                topics = topicHotel
            elif user_obj['propType'] == 'Restaurant':
                topics = topicRestaurant
            for x in topics:
                total_reviews_topic = collection.find({'Name': name, 'Place': place,
                                                       "Channel": ele["_id"]["Channel"],
                                                       x['topicName']: {'$ne': 3}}).count()
                postive_reviews_topic = collection.find({'Name': name, 'Place': place,
                                                         "Channel": ele["_id"]["Channel"],
                                                         x['topicName']: 1}).count()
                negative_reviews_topic = collection.find({'Name': name, 'Place': place,
                                                          "Channel": ele["_id"]["Channel"],
                                                          x['topicName']: 2}).count()
                neutral_reviews_topic = collection.find({'Name': name, 'Place': place,
                                                         "Channel": ele["_id"]["Channel"],
                                                         x['topicName']: 0}).count()
                if total_reviews_topic == 0:
                    CSI_topic = 0
                else:
                    CSI_topic = total_reviews_topic * 2 - (neutral_reviews_topic * 0.5) - negative_reviews_topic
                    CSI_topic /= total_reviews_topic * 2
                    CSI_topic *= 100.0
                data_topic.append(
                    {"topic": x['topicName'], "CSI_topic": round(CSI_topic, 2), "topicColor": x['topicColor']})

            repliednone = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R"}).count()
            repliednone1 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": ""}).count()
            replied0 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R0"}).count()
            replied1 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R1"}).count()
            replied2 = collection.find(
                {'Name': name, 'City': city, "Channel": ele["_id"]["Channel"], "Replied": "R2"}).count()

            if total_reviews == (repliednone + replied2 + repliednone1):
                mgtrespstr = "No"
            else:
                if total_reviews != 0:
                    mgtresp = round((replied1 / total_reviews) * 100, 2)
                    mgtrespstr = str(mgtresp) + "%"

            data.append(
                {"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"], "total_reviews": total_reviews,
                 "avg_rating": avg_rating, 'recommendation': round(avg_rating * 20, 2), "CSI": round(CSI, 2),
                 "pos_review": postive_reviews, "neu_review": neutral_reviews, "neg_review": negative_reviews,
                 "data_topic": data_topic, "data_rating": data_rating, "MgtResponse": mgtrespstr})

    return data
