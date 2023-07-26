### Run this file to create sql database ###

import sqlite3
import pandas as pd
import numpy as np

#Connect to the server
conn = sqlite3.connect('project')
c = conn.cursor()

## Parks Table & dataset ##

#Read master dataset
df = pd.read_csv('trails-data.csv')
#Create parks DataFrame
parks = df[['national_park']]
#Drop duplicates
parks = parks.drop_duplicates()
#Create a column that ranges from 1 to the maximum row
parks['park_id'] = range(1, len(parks)+1)
#Rename columns
parks = parks.rename(columns={'national_park':'parkName', 'park_id':'parkID'})
try:
    c.execute('DROP TABLE NationalParks;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE NationalParks (\
    parkName VARCHAR(100),\
    parkID INT PRIMARY KEY NOT NULL);')
parks.to_sql('NationalParks', conn, if_exists='append', index=False)

## Trails table & dataset
trails = df[['trail_id', 'name', 'national_park', 'length', 'elevation_gain',
       'difficulty_rating', 'route_type', 'num_reviews']]
trails = trails.rename(columns={'trail_id':'trailID', 'name':'trailName', 'national_park':'parkName', 'elevation_gain':'elevation_feet', 'difficulty_rating':'difficulty', 'route_type':'routeType', 'num_reviews':'reviews'})
trails = pd.merge(trails, parks, on='parkName')
trails.drop('parkName', axis=1, inplace=True)
trails['length'] = trails['length']*0.000621371
trails['trailID'].duplicated().any()
try:
    c.execute('DROP TABLE Trails;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Trails (\
    trailID INT PRIMARY KEY NOT NULL,\
    trailName VARCHAR(50) NOT NULL,\
    elevation_feet DECIMAL(10,4),\
    length DECIMAL(10,4),\
    difficulty INT,\
    routeType VARCHAR(20),\
    reviews INT,\
    parkID INT);')
trails.to_sql('Trails', conn, if_exists='append', index=False)

## Features Table & dataset ##

features = df[['trail_id', 'features']]
def format_text(text):
    text = text[1:-1].split(', ')
    new_string = [t.replace("'","") for t in text]
    return new_string
features['feature_list'] = features['features'].apply(format_text)
features.drop('features', axis=1, inplace=True)
new_rows = []
for _, row in features.iterrows():
    feature_list = row['feature_list']
    for feature in feature_list:
        new_rows.append([row['trail_id'], feature])

new_feature = pd.DataFrame(new_rows, columns=['trail_id', 'feature'])
new_feature.head()
new_feature.rename(columns={'trail_id':'trailID'}, inplace=True)
try:
    c.execute('DROP TABLE Features;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Features (\
    trailID INT, \
    feature VARCHAR(200),\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID) ON DELETE CASCADE);')
new_feature.to_sql('Features', conn, if_exists='append', index=False)

## Activities dataset ##
activities = df[['trail_id', 'activities']]
activities['activity_list'] = activities['activities'].apply(format_text)
activities.drop('activities', axis=1, inplace=True)
new_rows = []
for _, row in activities.iterrows():
    activity_list = row['activity_list']
    for activity in activity_list:
        new_rows.append([row['trail_id'], activity])

new_activities = pd.DataFrame(new_rows, columns=['trail_id', 'activity'])
new_activities.head()
new_activities.rename(columns={'trail_id':'trailID'}, inplace=True)
try:
    c.execute('DROP TABLE Activities;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Activities (\
    trailID INT, \
    activity VARCHAR(200),\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID) ON DELETE CASCADE);')
new_activities.to_sql('Activities', conn, if_exists='append', index=False)


## Location dataset ##

loc = df[['trail_id', 'city_name', 'state_name', '_geoloc']].rename(columns={'trail_id':'trailID', 'city_name':'area_name','state_name':'state', '_geoloc':'geolocation'})
try:
    c.execute('DROP TABLE Location;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Location (\
    trailID INT, \
    area_name VARCHAR(100),\
    state varchar(50),\
    geolocation varchar(100),\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID) ON DELETE CASCADE);')
loc.to_sql('Location', conn, if_exists='append', index=False)

## Users Table
try:
    c.execute('DROP TABLE Users;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Users (userID INTEGER PRIMARY KEY AUTOINCREMENT,\
    username VARCHAR(100),\
    uPassword VARCHAR(100));')


## TrailsUpdates Table ##

try:
    c.execute('DROP TABLE TrailsUpdates;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE TrailsUpdates (\
    updateID INTEGER PRIMARY KEY AUTOINCREMENT,\
    trailID INT,\
    userID INT,\
    content TEXT,\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID),\
    FOREIGN KEY (userID) REFERENCES Users (userID));')
