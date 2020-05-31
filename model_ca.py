from app import app
from flask import session
from .model_summary import getReviewCount
import json

topicHotel = ['All', 'Food', 'Service', 'Value', 'Ambience', 'Cleanliness', 'Amenities', 'Hospitality', 'Location',
              'Front-Desk', 'Room']

topicRestaurant = ['All', 'Taste', 'Variety', 'Drinks', 'Service', 'Value', 'Hygiene', 'Ambience', 'Hospitality',
                   'Comforts', 'Entertainment']


def competitive_index(start, end, topic):
    user_obj = session.get('user', None)
    if user_obj['propType'] == 'Hotel':
        connect = app.config['HOTEL_COLLECTION']
    elif user_obj['propType'] == 'Restaurant':
        connect = app.config['RESTAURANT_COLLECTION']
    data = competitveAnalysis(start, end, topic, connect)
    ol_list = data[0]['details']
    new_list =  [i for i in ol_list if i['Name'] is not None]
    data[0]['details'] = new_list
    return data


def topicrank(collection, topic, start, end):
    tags = collection.distinct("Name")
    place = collection.distinct("Place")
    user_obj = session.get('user', None)
    city_all = user_obj['City']
    city = user_obj['City_Name']
    al = list(collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "City": "$City"}}}]))
    data = []
    data1 = []
    for ele in al:
        name = ele["_id"]["Name"]
        place = ele["_id"]["Place"]
        total_reviews = collection.find(
            {'Name': name, 'Place': place, 'Date': {'$gte': start, '$lt': end}, topic: {'$ne': 3}}).count()
        total_reviews_pos = collection.find(
            {'Name': name, 'Place': place, 'Date': {'$gte': start, '$lt': end}, topic: 1}).count()
        total_reviews_Neg = collection.find(
            {'Name': name, 'Place': place, 'Date': {'$gte': start, '$lt': end}, topic: 2}).count()
        total_reviews_Neu = collection.find(
            {'Name': name, 'Place': place, 'Date': {'$gte': start, '$lt': end}, topic: 0}).count()
        if total_reviews != 0:
            CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
            CSI /= 2 * total_reviews
        else:
            CSI = 0
        data.append({'Hotel': name, 'Place': place, 'CSI': round(CSI, 2), "topic": topic})
    newlist = sorted(data, key=lambda k: k['CSI'], reverse=True)
    # user_obj = session.get('user', None)
    # name1 = user_obj['hotel']
    # place1 = user_obj['Place']
    # count = 0
    # for ele in newlist:
    #     if ele['Hotel'] == name1 and ele['Place']==place1:
    #         rank = count + 1
    #         break
    #     else:
    #         count = count + 1
    data1.append({"newlist": newlist})
    return data1


def overallrank(collection, start, end):
    tags = collection.distinct("Name")
    place = collection.distinct("Place")
    user_obj = session.get('user', None)
    city_all = user_obj['City']
    city = user_obj['City_Name']
    al = list(collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "City": "$City"}}}]))
    data = []
    data1 =[]
    for ele in al:
        name = ele["_id"]["Name"]
        place = ele["_id"]["Place"]
        total_reviews = collection.find(
            {'Name': name, 'Place': place, 'Sentiment': {'$ne': 3}, 'Date': {'$gte': start, '$lt': end}}).count()
        total_reviews_pos = collection.find(
            {'Name': name, 'Place': place, 'Sentiment': 1, 'Date': {'$gte': start, '$lt': end}}).count()
        total_reviews_Neg = collection.find(
            {'Name': name, 'Place': place, 'Sentiment': 2, 'Date': {'$gte': start, '$lt': end}}).count()
        total_reviews_Neu = collection.find(
            {'Name': name, 'Place': place, 'Sentiment': 0, 'Date': {'$gte': start, '$lt': end}}).count()
        if total_reviews != 0:
            CSI = (2 * total_reviews - (total_reviews_Neu * 0.5) - total_reviews_Neg) * 100.0
            CSI /= 2 * total_reviews
        else:
            CSI = 0
        data.append({'Hotel': name, 'Place': place, 'CSI': round(CSI, 2)})
    newlist = sorted(data, key=lambda k: k['CSI'], reverse=True)
    # user_obj = session.get('user', None)
    # name1 = user_obj['hotel']
    # place1 = user_obj['Place']
    # count = 0
    # for ele in newlist:
    #     #if ele['Hotel'] == name1 and ele['Place']==place1:
    #     if ele['Hotel'] == name1:
    #         rank = count + 1
    #         break
    #     else:
    #         count = count + 1
    data1.append({"newlist": newlist})
    return data1


def competitveAnalysis(start, end, topic, collection):
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    group = user_obj['group']
    if group != []:
        group.insert(0, {"Name": name, "Place": place})
    else:
        if name != "Ammi's Biryani" and name != "RICE BAR":
            group.insert(0, {"Name": name, "Place": place})
        else:
            al = list(
                collection.aggregate([{"$group": {"_id": {"Name": "$Name", "Place": "$Place", "City": "$City"}}}]))
            for i in al:
                nname = i["_id"]["Name"]
                if nname == name:
                    nplace = i["_id"]["Place"]
                    group.insert(0, {"Name": nname, "Place": nplace})
    city_all = user_obj['City']
    city = user_obj['City_Name']
    final_data = []
    func_ranking = overallrank(collection, start, end)
    newlist = func_ranking[0]['newlist']
    rankset_overall = []
    s = set()
    for i in newlist:
        s.add(i['CSI'])
    rankset_overall = sorted(s, reverse=True)
    all_data = []
    func_topic_ranking = topicrank(collection, topic, start, end)
    topic_newlist = func_topic_ranking[0]['newlist']
    rankset_topic = []
    s1 = set()
    for i in topic_newlist:
        s1.add(i['CSI'])
    rankset_topic = sorted(s1, reverse=True)
    if topic == 'All':
        for hotel in group:
            hname = hotel["Name"]
            hplace = hotel["Place"]
            total_reviews_present_month = getReviewCount(hname, hplace, None, start, end, None)
            positive_reviews_present_month = getReviewCount(hname, hplace, 1, start, end, None)
            negative_reviews_present_month = getReviewCount(hname, hplace, 2, start, end, None)
            neutral_reviews_present_month = getReviewCount(hname, hplace, 0, start, end, None)
            if total_reviews_present_month == 0:
                CSI_present_month = 0
            else:
                CSI_present_month = (2 * total_reviews_present_month - (
                    neutral_reviews_present_month * 0.5) - negative_reviews_present_month) * 100.0
                CSI_present_month /= 2 * total_reviews_present_month
            total_reviews_last_month = getReviewCount(hname, hplace, None, (2 * start - end), start, None)
            positive_reviews_last_month = getReviewCount(hname, hplace, 1, (2 * start - end), start, None)
            negative_reviews_last_month = getReviewCount(hname, hplace, 2, (2 * start - end), start, None)
            neutral_reviews_last_month = getReviewCount(hname, hplace, 0, (2 * start - end), start, None)
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
            count = 0
            for ele in newlist:
                    # if ele['Hotel'] == hname and ele['Place'] == hplace:
                    #     rank = count + 1
                    #     break
                    # else:
                    #     count = count + 1
                    if ele['Hotel'] == hname and ele['Place'] == hplace:
                        # rank = newlist.index(ele) + 1
                        for r in rankset_overall:
                            if r == ele['CSI']:
                                rank = rankset_overall.index(r) + 1
                                break
                            else:
                                count = count + 1
            all_data.append({'Topic': topic, 'Name': hname, 'Place': hplace, 'CSI': round(CSI_present_month, 2),
                                 'CSIchange': round(change, 2), 'csiUpDown': csiUpDown, 'csiClass': csiClass,
                                 'total_reviews': total_reviews_present_month,
                                 'Positive': positive_reviews_present_month, 'Negative': negative_reviews_present_month,
                                 'Neutral': neutral_reviews_present_month, 'Rank': rank})
        final_data.append({'category': topic, 'details': all_data})
    else:
        for hotel in group:
            hname = hotel["Name"]
            hplace = hotel["Place"]
            total_reviews_present_month = collection.find({'Name': hname, 'Place': hplace,
                                                               'Date': {'$gte': start, '$lt': end},
                                                               topic: {'$ne': 3}}).count()
            positive_reviews_present_month = collection.find({'Name': hname, 'Place': hplace,
                                                                  'Date': {'$gte': start, '$lt': end},
                                                              topic: 1}).count()
            negative_reviews_present_month = collection.find({'Name': hname, 'Place': hplace,
                                                                  'Date': {'$gte': start, '$lt': end},
                                                              topic: 2}).count()
            neutral_reviews_present_month = collection.find({'Name': hname, 'Place': hplace,
                                                                 'Date': {'$gte': start, '$lt': end},
                                                             topic: 0}).count()
            if total_reviews_present_month == 0:
                CSI_present_month = 0
            else:
                CSI_present_month = (2 * total_reviews_present_month - (
                    neutral_reviews_present_month * 0.5) - negative_reviews_present_month) * 100.0
                CSI_present_month /= 2 * total_reviews_present_month
            total_reviews_last_month = collection.find({'Name': hname, 'Place': hplace,
                                                            'Date': {'$gte': 2 * start - end, '$lt': start},
                                                            topic: {'$ne': 3}}).count()
            positive_reviews_last_month = collection.find({'Name': hname, 'Place': hplace,
                                                               'Date': {'$gte': 2 * start - end, '$lt': start},
                                                           topic: 1}).count()
            negative_reviews_last_month = collection.find({'Name': hname, 'Place': hplace,
                                                               'Date': {'$gte': 2 * start - end, '$lt': start},
                                                           topic: 2}).count()
            neutral_reviews_last_month = collection.find({'Name': hname, 'Place': hplace,
                                                              'Date': {'$gte': 2 * start - end, '$lt': start},
                                                          topic: 0}).count()
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
            count = 0
            for ele in topic_newlist:
                    # if ele['Hotel'] == hname and ele['Place'] == hplace:
                    #     rank = count + 1
                    #     break
                    # else:
                    #     count = count + 1
                    if ele['Hotel'] == hname and ele['Place'] == hplace:
                        # rank = topic_newlist.index(ele) + 1
                        for r in rankset_topic:
                            if r == ele['CSI']:
                                rank = rankset_topic.index(r) + 1
                                break
                            else:
                                count = count + 1
            all_data.append({'Topic': topic, 'Name': hname, 'Place': hplace, 'CSI': round(CSI_present_month, 2),
                                 'CSIchange': round(change, 2), 'csiUpDown': csiUpDown, 'csiClass': csiClass,
                                 'total_reviews': total_reviews_present_month,
                                 'Positive': positive_reviews_present_month, 'Negative': negative_reviews_present_month,
                                 'Neutral': neutral_reviews_present_month, 'Rank': rank})
        final_data.append({'category': topic, 'details': all_data})
    return final_data
