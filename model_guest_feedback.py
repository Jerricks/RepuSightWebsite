from flask import request

topics = ['$taste' , '$variety' , '$experience' , '$services' , '$value' , '$hygiene' , '$ambience' , '$hospitality' , '$quantity' , '$satisfaction']
def rating_by_dist(coll):
    ratings = [1 , 2,3,4,5]
    ratings_dist = {}
    for rating in ratings:
        ratings_dist[rating] = 0
        for topic in topics:
            topic = topic.strip('$')
            ratings_dist[rating] += coll.find({'propertyName' : request.session['user']['hotel']  , topic : rating}).count()

    return ratings_dist

def send_total_score(coll):
    a = coll.aggregate([{
        '$project':{
            'total_score':{'$avg' : topics}
        }
    }])

    return a

def rating__by_topic():
    pass