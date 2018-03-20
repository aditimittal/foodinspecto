#!/usr/bin/env python
#This file keeps on updating the current stored data.
from pyzomato import Pyzomato
import nltk
import re
import urllib2, json, sys
from textblob import TextBlob
import pymongo
import unicodedata
import sys
from pymongo import MongoClient

client = MongoClient()
client = MongoClient('127.0.0.1', 27017)
db = client.restaurants_database
p = Pyzomato('fbde89c2e30ec611b531a3a17c7eeca3')
# m stores name of all tables
m=[]
for i in tab:
	m.append(i.encode("UTF-8"))

for postsss in m:
	val=postsss[5:]  #table10 gives 10 which is used as city id
	db[postsss]drop() #drops the current table
	res_url="https://api.zomato.com/v1/directory.json?city_id="+str(val)+"&count=94&apikey=16b682609de39e187aceba2cafcaaa5d"
	#Update the database for the dropped table by using its city id.

	requestss = urllib2.Request(res_url)
	rest = urllib2.urlopen(requestss)
	json_rest = json.load(rest)
	restaurants=json_rest['results']
	for i in restaurants:
		collection = db.city_id
		negative_count=0
		positive_count=0
		restaurant_id= i['restaurant']['res_id']
		url="https://api.zomato.com/v1/reviews.json/"+str(restaurant_id)+"/user?count=0&apikey=16b682609de39e187aceba2cafcaaa5d"
		req = urllib2.Request(url)
		restt = urllib2.urlopen(req)

		json_data = json.load(restt)
		revjjsjs=json_data['userReviews']
		url_det="https://api.zomato.com/v1/restaurant.json/"+str(restaurant_id)+"?apikey=a54e351eb6f630cb9ed6f8efe31e0c1e"
		requesting = urllib2.Request(url_det)

		results_rest = urllib2.urlopen(requesting)
		json_data = json.load(results_rest)
		link=json_data['userReviews']['review_url']
		name=json_data['name']
		address=json_data['location']['address']
		debt=p.getRestaurantDetails(restaurant_id)
		image=debt['thumb']
		user_rating=debt['user_rating']['aggregate_rating']
	
		for i in revjjsjs:			
			m=i['review']
			t=m['reviewText']
			t=t.encode('unicode-escape')
			txt=t
			if(txt!=None):
				blob = TextBlob(txt)
				for sentence in blob.sentences:
					
					if(sentence.sentiment.polarity>0):
						positive_count+=1
						
					else:
						negative_count+=1
		restaurant_rating_ratio=(negative_count/float(positive_count))
		document={
		'restid':restaurant_id,
		'rest_name':name,
		'address':address,
		'rating':user_rating,
		'ratio':restaurant_rating_ratio,
		'img_url':image,
		'pos':positive_count,
		'neg':negative_count,
		'review_link':link
		};

		result=db[postsss].insert_one(document) #stores the document in the table
docs=db[postsss].find().sort("ratio",pymongo.DESCENDING) #sort in desc order of ratio that is restaurant with higher negative to positive ratio is at top.