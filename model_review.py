from app import app
from flask import session
from pymongo import DESCENDING
from .model_summary import check_collection
import datetime as dtm
from nltk import word_tokenize, FreqDist, pos_tag, bigrams
from nltk.corpus import stopwords
from string import punctuation


def sources():
    collection = check_collection()
    user_obj = session.get('user', None)
    name = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    nintydays = dtm.date.today() - dtm.timedelta(40)
    startDate = int(nintydays.strftime("%s"))
    endDate = int(dtm.date.today().strftime("%s"))
    nocomment = ["No Comment", "No Comments", "There are no comments available for this review", "Comment not posted",
                 "no comment had been posted"]
    data = []
    if city_all == "True":
        data = list(collection.aggregate(
            [{"$match": {"Name": name, "City": city, 'Comment': {'$nin': nocomment},
                         'Date': {'$gte': startDate, '$lt': endDate}}},
             {"$group": {"_id": {"Name": name, "City": city, "Channel": "$Channel", "icon": "$icon"}}}]))
    else:
        data = list(collection.aggregate([{"$match": {"Name": name, "Place": place, 'Comment': {'$nin': nocomment},
                                                      'Date': {'$gte': startDate, '$lt': endDate}}}, {"$group": {
            "_id": {"Name": name, "Place": place, "Channel": "$Channel", "icon": "$icon"}}}]))
    return data


def getReview():
    collection = check_collection()
    user_obj = session.get('user', None)
    hotels = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    nintydays = dtm.date.today() - dtm.timedelta(40)
    startDate = int(nintydays.strftime("%s"))
    endDate = int(dtm.date.today().strftime("%s"))
    nocomment = ["No Comment", "No Comments", "There are no comments available for this review", "Comment not posted",
                 "no comment had been posted"]
    if city_all == "True":
        data = list(collection.find({'Name': hotels, 'City': city, 'Comment': {'$nin': nocomment},
                                     'Date': {'$gte': startDate, '$lt': endDate}}).sort("Date", DESCENDING))
    else:
        data = list(collection.find({'Name': hotels, 'Place': place, 'Comment': {'$nin': nocomment},
                                     'Date': {'$gte': startDate, '$lt': endDate}}).sort("Date", DESCENDING))
    return data


def cleanText(text):
    text = text.lower()
    default_stopwords = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [word for word in words if not word in default_stopwords]
    words = pos_tag(words)
    words = [word for word, pos in words if
             (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS' or pos == 'JJR' or pos == 'JJS')]
    words = [word for word in words if not all(char in punctuation for char in words)]
    words = [word for word in words if word not in default_stopwords]
    words = bigrams(words)
    fdist = FreqDist(words)
    lst = []
    for word, frequency in fdist.most_common(5):
        word = ' '.join(str(i) for i in word)
        lst.append({'text': word, 'weight': frequency})
    return lst


def summaryKeywords():
    collection = check_collection()
    user_obj = session.get('user', None)
    hotels = user_obj['hotel']
    place = user_obj['Place']
    city_all = user_obj['City']
    city = user_obj['City_Name']
    nintydays = dtm.date.today() - dtm.timedelta(40)
    startDate = int(nintydays.strftime("%s"))
    endDate = int(dtm.date.today().strftime("%s"))
    if city_all == "True":
        totalPositiveReviews = list(
            collection.find({'Name': hotels, 'City': city, 'Sentiment': 1, 'Date': {'$gte': startDate, '$lt': endDate}},
                            {"Comment": 1, "_id": 0}))
        final_text = ''
        for comment in totalPositiveReviews:
            final_text = final_text + str(comment['Comment'])
        positiveList = cleanText(final_text)
        totalNegativeReviews = list(
            collection.find({'Name': hotels, 'City': city, 'Sentiment': 2, 'Date': {'$gte': startDate, '$lt': endDate}},
                            {"Comment": 1, "_id": 0}))
        final_text = ''
        for comment in totalNegativeReviews:
            final_text = final_text + str(comment['Comment'])
        negativeList = cleanText(final_text)
    else:
        totalPositiveReviews = list(collection.find(
            {'Name': hotels, 'Place': place, 'Sentiment': 1, 'Date': {'$gte': startDate, '$lt': endDate}},
            {"Comment": 1, "_id": 0}))
        final_text = ''
        for comment in totalPositiveReviews:
            final_text = final_text + str(comment['Comment'])
        positiveList = cleanText(final_text)
        totalNegativeReviews = list(collection.find(
            {'Name': hotels, 'Place': place, 'Sentiment': 2, 'Date': {'$gte': startDate, '$lt': endDate}},
            {"Comment": 1, "_id": 0}))
        final_text = ''
        for comment in totalNegativeReviews:
            final_text = final_text + str(comment['Comment'])
        negativeList = cleanText(final_text)
    data = [{"positiveList": positiveList}, {"negativeList": negativeList}]
    return data
