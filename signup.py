#!/usr/bin/env python
#import pymongo
import cgi, cgitb 
import site
site.addsitedir('/Users/Aditi/miniconda3/lib/python2.7/site-packages')
import pymongo
from pymongo import MongoClient

client = MongoClient()
client = MongoClient('127.0.0.1', 27017)
db = client.restaurants_database

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

inspector_name = form.getvalue('inspector_name')
inspector_id = form.getvalue('inspector_id')
password = form.getvalue('password')

print "Content-type:text/html"
print 
print "<html>"
print "<head>"
print "</head>"
print "<body style='background-color:#ADD8E6;'>"


document={
        'insp_name':inspector_name,
        'insp_id':inspector_id,
        'password':password
        };

if db.signup.find({'insp_id':inspector_id},{'password':password}).count()>0:
    print "Credentials already in use"
else:
    result=db.signup.insert_one(document)
    print "Successfuly signed up"


print "<form action = 'signup.html' method = 'post'><input type = 'submit' value = 'Go Back' /></form>"
print "</body>"
print "</html>"
