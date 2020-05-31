from app import app
from flask import session
import datetime as dtm
import time, json
from nltk import word_tokenize, FreqDist, pos_tag, tokenize, bigrams, data
from nltk.corpus import stopwords
from string import punctuation
import requests
from textblob import TextBlob
import re
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from flask import abort
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/56.0.2924.87")


headers = {
  "User-Agent" : "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
}



def sentiment_analyzer(text):
    text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
    text = ' '.join([word for word in text.split() if word not in (stopwords.words('english'))])
    blob = TextBlob(text)
    if blob.sentiment.polarity > 0.4:
        sentiment="Positive"
    elif blob.sentiment.polarity > 0.0 and blob.sentiment.polarity <= 0.4:
        sentiment="Neutral"
    else:
        sentiment="Negative"
    return sentiment


def instagram():
    connect = app.config['SOCIALMEDIADATA_COLLECTION']
    user_obj = session.get('user', None)
    hotel = user_obj['hotel']
    place = user_obj['Place']
    data = list(connect.find({'hotel': hotel, 'Place': place}))
    instakey = data[0]['instagramkeyword']
    if instakey != "":
        url1 = "https://www.instagram.com/{}/".format(instakey)
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true'])
        driver.get(url1)
        time.sleep(1)
        driver.maximize_window()
        # followers = driver.find_element_by_xpath("//*[@id='react-root']/section/main/article/header/div[2]/ul/li[2]/span/span").text
        # following = driver.find_element_by_xpath("//*[@id='react-root']/section/main/article/header/div[2]/ul/li[3]/span/span").text
        followers = 0
        following = 0
        driver.close()
        url = "http://instagram.com/explore/tags/{}/".format(instakey)
        r = requests.get(url, headers=headers)
        text = (r.text)
        left = text.index('window._sharedData') + 21
        right = text.index(';</script>')
        text = text[left:right]
        tmp = json.loads(text)
        JSON1 = []
        total_inst = 0
        total_inst_pos = 0
        total_inst_neg = 0
        total_inst_neu = 0
        totallikes = 0
        name = str(tmp['entry_data']['TagPage'][0]['tag']['name'])
        for obj in tmp['entry_data']['TagPage'][0]['tag']['media']['nodes']:
            total_inst = total_inst + 1
            cur = {}
            cur['date'] = obj['date']
            cur['total_comments'] = obj['comments']['count']
            cur['total_likes'] = obj['likes']['count']
            cur['is_video'] = obj['is_video']
            cur['caption'] = str(obj['caption'])
            link = obj['display_src']
            link = link.split('?',1)[0]
            cur['image_url'] = link
            cur['code'] = obj['code']
            cur['sentiment'] = str(sentiment_analyzer(str(obj['caption'])))
            if cur['sentiment'] == 'Positive':
                total_inst_pos = total_inst_pos + 1
            elif cur['sentiment'] == 'Neutral':
                total_inst_neu = total_inst_neu + 1
            else:
                total_inst_neg = total_inst_neg + 1
            totallikes += cur['total_likes']
            JSON1.append({"name": name,"date":cur['date'], 'total_comments': cur['total_comments'],"total_likes":cur['total_likes'],'is_video':cur['is_video'],'caption':cur['caption'],'image_url':cur['image_url'],'code':cur['code'], 'sentiment': cur['sentiment']})
        data = [{'data':JSON1, "socialchannel": "Instagram", "totalInst":{'total_inst':total_inst, 'total_inst_pos': total_inst_pos, 'total_inst_neu':total_inst_neu, 'total_inst_neg':total_inst_neg}, "imgPath":"/static/images/instagram.png", "totalLikes":totallikes, "following": following, "followers": followers}]
    else:
        data = [{"socialchannel": "Instagram", "totalInst": {'total_inst': 0, 'total_inst_pos': 0,
                                              'total_inst_neu': 0, 'total_inst_neg': 0},
                 "totalLikes":0, "following": 0, "followers": 0,
                 "imgPath": "/static/images/instagram.png"}]
    return data


def facebook():
    connect = app.config['SOCIALMEDIADATA_COLLECTION']
    user_obj = session.get('user', None)
    hotel = user_obj['hotel']
    place = user_obj['Place']
    data = list(connect.find({'hotel': hotel, 'Place': place}))
    fbkey = data[0]['fbkeyword']
    if fbkey != "":
        url = "https://graph.facebook.com/{0}/?fields=fan_count,talking_about_count,rating_count,checkins,overall_star_rating,feed.limit(100){{name,message,picture,type,link,likes.limit(0).summary(true),shares,comments.limit(0).summary(true)}},picture&access_token={1}".format(
            fbkey,app.config["FB_TOKEN"])
        #r = requests.get(url, headers=headers)
        r = requests.get(url)
        data = json.loads((r.text))
        JSON = []
        total_fb = 0
        total_fb_pos = 0
        total_fb_neg = 0
        total_fb_neu = 0
        if 'error' in data.keys():
            raise abort(500)
        for d in data["feed"]["data"]:
            total_fb = total_fb + 1
            cur = {}
            if "name" in d:
                cur['name'] = str(d['name'])
            else:
                cur['name'] = None
            if "picture" in d:
                cur['picture'] = str(d['picture'])
            else:
                cur['picture'] = None
            if "link" in d:
                cur['link'] = str(d['link'])
            else:
                cur['link'] = None
            if 'message' in d:
                cur['message'] = str(d['message'])
            else:
                cur['message'] = None
            if 'shares' in d:
                cur['shares'] = d['shares']['count']
            else:
                cur['shares'] = 0
            if 'likes' in d:
                cur['total_likes'] = d['likes']['summary']['total_count']
            else:
                cur['total_likes'] = 0
            if 'comments' in d:
                cur['total_comments'] = d['comments']['summary']['total_count']
            else:
                cur['total_comments'] = 0
            if 'message' in d:
                cur['sentiment'] = str(sentiment_analyzer(str(d['message'])))
            else:
                cur['sentiment'] = None
            if cur['sentiment'] == 'Positive':
                total_fb_pos = total_fb_pos + 1
            elif cur['sentiment'] == 'Neutral':
                total_fb_neu = total_fb_neu + 1
            else:
                total_fb_neg = total_fb_neg + 1
            JSON.append({'name': cur['name'],'picture': cur['picture'],"link":cur['link'],'message':cur['message'],'shares':cur['shares'],'total_likes':cur['total_likes'],'total_comments':cur['total_comments'], 'sentiment':cur['sentiment']})
        data = [{"data":JSON,"user_picture":data['picture'],"fan_count":data['fan_count'],"talking_about_count":data['talking_about_count'],"rating_count":data['rating_count'],"checkins":data['checkins'],"overall_star_rating":data['overall_star_rating'], "socialchannel": "Facebook", "totalFb":{'total_fb':total_fb, 'total_fb_pos': total_fb_pos, 'total_fb_neu':total_fb_neu, 'total_fb_neg':total_fb_neg}, "imgPath":"/static/images/fb.png"}]
    else:
        data = [{"socialchannel": "Facebook", "totalFb": {'total_fb': 0, 'total_fb_pos': 0,
                                              'total_fb_neu': 0, 'total_fb_neg': 0},
                 "fan_count": 0, "talking_about_count": 0, "checkins":0,
                 "imgPath": "/static/images/fb.png"}]
    return data


def twitter():
    connect = app.config['SOCIALMEDIADATA_COLLECTION']
    user_obj = session.get('user', None)
    hotel = user_obj['hotel']
    place = user_obj['Place']
    data = list(connect.find({'hotel': hotel, 'Place': place}))
    twitterkey = data[0]['twitterkeyword']
    if twitterkey != "":
        username = '%23' + twitterkey.lower()
        r = requests.get('https://twitter.com/search?f=tweets&vertical=default&q={}'.format(username), headers=headers)
        time.sleep(5)
        soup = BeautifulSoup(str(r.text).encode("utf-8"), "lxml")
        JSON = []
        total_tw = 0
        total_tw_pos = 0
        total_tw_neg = 0
        total_tw_neu = 0
        lis = soup.find_all('li', class_='js-stream-item')
        for obj in lis:
            total_tw = total_tw + 1
            cur = {}
            cur['username'] = str(obj.find_all('strong', class_='fullname')[0].text)
            cur['Rimg'] = obj.find_next('img', class_='avatar')['src']
            cur['tweet'] = str(obj.find_all('p', class_="tweet-text")[0].text)
            cur['time'] = str(obj.find_all('a', class_="tweet-timestamp")[0]['title'])
            cur['link'] = "https://twitter.com" + str(obj.find_all('a', class_="tweet-timestamp")[0]['href'])
            cur['total_retweets'] = str(obj.find_all('span', class_="ProfileTweet-actionCountForAria")[0].text)
            cur['total_likes'] = str(obj.find_all('span', class_="ProfileTweet-actionCountForAria")[1].text)
            cur['sentiment'] = str(sentiment_analyzer(str(obj.find_all('p', class_="tweet-text")[0].text)))
            if cur['sentiment'] == 'Positive':
                total_tw_pos = total_tw_pos + 1
            elif cur['sentiment'] == 'Neutral':
                total_tw_neu = total_tw_neu + 1
            else:
                total_tw_neg = total_tw_neg + 1
            JSON.append({"username":cur['username'], "Rimg":cur['Rimg'],"tweet":cur['tweet'],'time':cur['time'],'link':cur['link'],'total_retweets':cur['total_retweets'],'total_likes':cur['total_likes'], 'sentiment': cur['sentiment']})
        username1 = '%40' + twitterkey.lower()
        r1 = requests.get('https://twitter.com/search?f=tweets&vertical=default&q={}'.format(username1), headers=headers)
        soup1 = BeautifulSoup(str(r1.text).encode("utf-8"), "lxml")
        lis1 = soup1.find_all('li', class_='js-stream-item')
        for obj in lis1:
            total_tw = total_tw + 1
            cur = {}
            cur['username'] = str(obj.find_all('strong', class_='fullname')[0].text)
            cur['Rimg'] = obj.find_next('img', class_='avatar')['src']
            cur['tweet'] = str(obj.find_all('p', class_="tweet-text")[0].text)
            cur['time'] = str(obj.find_all('a', class_="tweet-timestamp")[0]['title'])
            cur['link'] = "https://twitter.com" + str(obj.find_all('a', class_="tweet-timestamp")[0]['href'])
            total_retweets = str(obj.find_all('span', class_="ProfileTweet-actionCountForPresentation")[1].text)
            if total_retweets == '':
                cur['total_retweets'] = 0
            else:
                cur['total_retweets'] = total_retweets
            total_likes = str(obj.find_all('span', class_="ProfileTweet-actionCountForPresentation")[2].text)
            if total_likes=='':
                cur['total_likes'] = 0
            else:
                cur['total_likes'] = total_likes
            cur['sentiment'] = str(sentiment_analyzer(str(obj.find_all('p', class_="tweet-text")[0].text)))
            if cur['sentiment'] == 'Positive':
                total_tw_pos = total_tw_pos + 1
            elif cur['sentiment'] == 'Neutral':
                total_tw_neu = total_tw_neu + 1
            else:
                total_tw_neg = total_tw_neg + 1
            JSON.append({"username":cur['username'], "Rimg":cur['Rimg'],"tweet":cur['tweet'],'time':cur['time'],'link':cur['link'],'total_retweets':cur['total_retweets'],'total_likes':cur['total_likes'], 'sentiment': cur['sentiment']})
        r1 = requests.get('https://twitter.com/{}'.format(twitterkey), headers=headers)
        soup1 = BeautifulSoup(str(r1.text).encode("utf-8"), "lxml")
        no_of_post = soup1.find('li', class_='ProfileNav-item--tweets')
        no_of_post = no_of_post.find('span', class_='ProfileNav-value').text
        no_of_following = soup1.find('li', class_='ProfileNav-item--following')
        no_of_following = no_of_following.find('span', class_='ProfileNav-value').text
        no_of_followers = soup1.find('li', class_='ProfileNav-item--followers')
        no_of_followers = no_of_followers.find('span', class_='ProfileNav-value').text
        no_of_favorites = soup1.find('li', class_='ProfileNav-item--favorites')
        no_of_favorites = no_of_favorites.find('span', class_='ProfileNav-value').text
        data = [{"data": JSON, "post":no_of_post, "following":no_of_following, "followers":no_of_followers, "likes":no_of_favorites, "socialchannel": "Twitter", "totalTw":{'total_tw':total_tw, 'total_tw_pos': total_tw_pos, 'total_tw_neu':total_tw_neu, 'total_tw_neg':total_tw_neg},"imgPath":"/static/images/twitter.png"}]
    else:
        data = [{"socialchannel": "Twitter", "totalTw": {'total_tw': 0, 'total_tw_pos': 0,
                                              'total_tw_neu': 0, 'total_tw_neg': 0},
                 "post": 0, "following": 0, "followers": 0,
                 "likes": 0,
                 "imgPath": "/static/images/twitter.png"}]
    return data



