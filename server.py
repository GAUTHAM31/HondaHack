import mysql.connector
import os
import json
from dotenv import load_dotenv
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from geopy.geocoders import Nominatim

load_dotenv()

# Data Base
mydb = mysql.connector.connect(
  host=os.getenv('LOCALHOST'),
  user=os.getenv('DB_USER'),
  password=os.getenv('DB_PASSWORD'),
  database=os.getenv('DB_NAME'),
  auth_plugin=os.getenv('DB_AUTH')
)

mycursor = mydb.cursor()

# Rest API for Alexa skill
app = Flask(__name__)
api = Api(app)

# GeoPy Config
geolocator = Nominatim(user_agent="honda_app")


# API for getting nearest parking location
@app.route("/park/<location>", methods=["GET"])
def setName(location):
    if request.method=='GET':
      lat, longt = getLatLong(location)
      mycursor.execute("SELECT Latitude, Longitude, LocationID from LocationTable where score > 20")
      shortest = 0
      locid = 0
      shortestLong = 0
      shortestLat = 0
      for (Latitude, Longitude, LocationID) in mycursor:
        # calculate shortest distance
        dist = haversine(longt, lat,Longitude, Latitude)
        if dist < shortest:
          shortest = dist
          locid = LocationID
          shortestLat = Latitude
          shortestLong = Longitude
        results = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + shortestLat + "," + shortestLong + "&radius=150&key=" + os.getenv('GOOGLE_MAP_API_KEY'))
        landmarks = results['results'] 
      return jsonify(str("The best possible parking spot is " + shortest + " meters near " + landmarks[0]['name']))

# API for getting marking the current location as parking spot
@app.route("/mark-parking-spot/<lat>,<longt>", methods=["GET"])
def markParking(lat, longt):
    if request.method=='GET':
      return jsonify(str("Sucessfully marked your current location as a parking spot"))


if __name__ == '__main__':
    app.run(debug=True)

def generateScore(data, locationid):
  score = 0
  # Check if car is in Parking Brake is On
  score = score + 50 if data['ParkBrake'] == "On" else score 
  # Check if car's parking sensors where on
  score = score + 20 if data['ParkSensor'] == "On" else score 
  # Check if the car is parked in a location for a long time
  mycursor.execute("select LocationTime from LocationTable as l INNER JOIN CarTable as c ON l.LocationID =c.LocationID where CarID= "+ str(data['CarID']) +" Order by l.LocationID DESC limit 2;")
  mycursor.fetchall()
  time1, time2 = ['2020-12-20 15:04:38', '2020-12-20 15:01:36']
  date_time_obj = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
  date_time_obj2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
  diff = date_time_obj - date_time_obj2
  min = divmod(diff.total_seconds(), 60)[0]
  if min > 10 and min < 60:
    score = score + 30
  # Check if the car is in Parking Mode
  score = score + 20 if data['ParkMode'] == "On" else score 
  # Check if multiple people have parked here
  # Check DB if there are record around this area
  mycursor.execute("select count(1) from LocationTable where CAST(Latitude AS DECIMAL) = CAST("+ str(data['latitude'])+" AS DECIMAL)")
  otherUsers = mycursor.fetchone()[0]
  score = (otherUsers -1) * 40
  print(score)
  # Check if traffic is okey
  # Check if the location is in road side

  mycursor.execute("update LocationTable set score = 10 where LocationID = " + locationid )
  mydb.commit()

def insertIntoDB(data):
    insertQuery = str(data['latitude']) + ',' + str(data['longitude']) + ',' + str(0)
    mycursor.execute("INSERT INTO LocationTable (Latitude, Longitude, Score ) Values (" + insertQuery + ")")
    mycursor.execute("SELECT LAST_INSERT_ID();")
    locationid = mycursor.fetchone()[0]
    mycursor.execute("INSERT INTO CarTable Values ( " + str(locationid) +", "+ str(data['CarID']) + ",\""+ data['ParkBrake'] + '\",\"' + data['ParkSensor'] + '\",\"' + data['ParkMode']+"\","+ str(data['EngineStart'])+")")
    mydb.commit()
    generateScore(data, locationid)

def getAPIData():
  # Ideally this should be api from the car
    car_data =  '{ "latitude": 12.911913, "longitude":77.649561, "ParkBrake":"ON", "ParkSensor": "ON","ParkMode": "OFF", "CarID": 53248, "EngineStart": false}'
    return json.loads(car_data)

def haversine(lon1, lat1, lon2, lat2):
  """
  Calculate the great circle distance between two points 
  on the earth (specified in decimal degrees)
  """
  # convert decimal degrees to radians 
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  # haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a)) 
  # Radius of earth in kilometers is 6371
  km = 6371* c
  return km
    
def getLatLong(locationName):
  # Can you current Location from CarData
  location = geolocator.geocode(locationName + "India")
  return location.latitude, location.longitude

def markPlaceAsParkable(latitude, longitude):
  mycursor.execute("Update LocationTable Set Score = 500 where  CAST(Latitude AS DECIMAL) = CAST("+ str(latitude)+" AS DECIMAL) and CAST(Longitude AS DECIMAL) = CAST("+ str(longitude)+" AS DECIMAL)")
  mydb.commit()
# insertIntoDB(getAPIData())