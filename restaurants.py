#!/usr/bin/env python

import cgi, cgitb 
import site
site.addsitedir('/Users/Aditi/miniconda3/lib/python2.7/site-packages')
from pyzomato import Pyzomato
import nltk
import re
import urllib2, json, sys
from textblob import TextBlob
import pymongo
import unicodedata
import sys
from pymongo import MongoClient
#database
client = MongoClient()
client = MongoClient('127.0.0.1', 27017)
db = client.restaurants_database
p = Pyzomato('a54e351eb6f630cb9ed6f8efe31e0c1e')

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
city_name = form.getvalue('city_name')
country_name = form.getvalue('country_name')

city=p.getCityDetails(q=city_name)
location= city['location_suggestions']
tab=db.collection_names()
m=[]
for i in tab:
	m.append(i.encode("UTF-8"))

print "Content-type:text/html"
print 
print "<html>"
print "<head>"
print "<title>Welcome</title>"
print "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>"
print "<style>tr,td{padding:20px; transition: max-height 1s ease-in-out;} tr:nth-child(even){background-color: lightgreen;} tr:nth-child(even):hover{background-color:limegreen} tr:nth-child(odd):hover{background-color:lightgray} tr{width:150px;} tr:hover .imgi{width:200px;} .navbar{background-color:#4CAF50; font-color:white;} .footer {left: 0;bottom: 0;width: 100%;background-color: #4CAF50;color: white;text-align: center;}</style>"

print "</head>"
print "<body >"

for i in location:
	#check for city id with same country name
	if((i['country_name'].lower())==country_name.lower()):
		city_id= i['id']
postsss="table"+str(city_id)
if postsss in m:
	print "<p></p>"
	
else:
	#get all the restaurants details from the zomato api
	res_url="https://api.zomato.com/v1/directory.json?city_id="+str(city_id)+"&count=30&apikey=a54e351eb6f630cb9ed6f8efe31e0c1e"

	requestss = urllib2.Request(res_url)
	rest = urllib2.urlopen(requestss)
	json_rest = json.load(rest)
	restaurants=json_rest['results']
	for i in restaurants:
		collection = db.city_id
		negative_count=0
		positive_count=0
		#get restaurant id
		restaurant_id= i['restaurant']['res_id']
		#get user reviews of particular restaurant
		url="https://api.zomato.com/v1/reviews.json/"+str(restaurant_id)+"/user?count=0&apikey=a54e351eb6f630cb9ed6f8efe31e0c1e"
		req = urllib2.Request(url)
		restt = urllib2.urlopen(req)

		json_data = json.load(restt)
		review_count=json_data['reviewsCount']
		#get restaurant details using restaurant id
		url_det="https://api.zomato.com/v1/restaurant.json/"+str(restaurant_id)+"?apikey=a54e351eb6f630cb9ed6f8efe31e0c1e"
		requesting = urllib2.Request(url_det)
		results_rest = urllib2.urlopen(requesting)
		json_dat = json.load(results_rest)
		link=json_dat['userReviews']['review_url']
		name=json_dat['name']
		address=json_dat['location']['address']
		debt=p.getRestaurantDetails(restaurant_id)
		#get image icon of restaurant id
		image=debt['thumb']
		user_rating=debt['user_rating']['aggregate_rating']
		if review_count==0:
			pass
		else:
			revjjsjs=json_data['userReviews']
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
				else:
					pass

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
			result=db[postsss].insert_one(document)
docs=db[postsss].find().sort("ratio",pymongo.DESCENDING)
#navbar
print "<nav class='navbar navbar-inverse'>"
print "  <div class='container-fluid'>"
print "    <div class='navbar-header'>"
print "      <a class='navbar-brand' href='hello.html' style='color:white'>FOODINSPECTO</a>"
print  "    </div>"
print "    <ul class='nav navbar-nav navbar-right'>"
print "      <li><a href='hello.html' style='color:white'>Home</a></li>"
print "      <li><a href='login.html' style='color:white'>Sign Out</a></li>"
print "    </ul>"
print "  </div>"
print "</nav>"

print"<center><br><br><h1 style='color:teal'>LIST OF RESTAURANTS</h1></center>"
print "<div id='restaurants'>" 
print"<center><table style='cellpadding: 10;'>"

for i in docs:

	if i['img_url']=="":
		i['img_url']="https://media.licdn.com/mpr/mpr/AAEAAQAAAAAAAAjZAAAAJGZkYzRiZDVmLWY0NDUtNGNiZi04NzFhLTc1YTIyMzY0MzhhOQ.jpg"
		print "<tr><td><img style='height:150px;width:150px;' id='imgi' src='%s'></td><td><b>%s</b><br>%s<br>%s<br><br><a href='%s'><input type='button' value='Problems' style='font-size:15px'></a></td><td>Rating: %s</td></tr>"%(i['img_url'],i['rest_name'],i['address'],round(i['ratio'],2),i['review_link'],i['rating'])

	else:
		print "<tr><td><img style='height:150px;width:150px;' id='imgi' src='%s'></td><td><b>%s</b><br>%s<br>%s <br><br><a href='%s'><input type='button' value='Problems' style='font-size:15px'></a></td><td>Rating: %s</td></tr></center>"%(i['img_url'],i['rest_name'],i['address'],round(i['ratio'],2),i['review_link'],i['rating'])
print"</table></div>"
print "<div class='footer'>"
print " <p>Copyright. www.semicolon.com</p>"
print "</div>"
print "<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>"
print "<script src='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'></script>"
print "</body>"
print "</html>"