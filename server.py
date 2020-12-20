import mysql.connector
import os
from dotenv import load_dotenv
import json

load_dotenv()

mydb = mysql.connector.connect(
  host=os.getenv('LOCALHOST'),
  user=os.getenv('DB_USER'),
  password=os.getenv('DB_PASSWORD'),
  database=os.getenv('DB_NAME'),
  auth_plugin=os.getenv('DB_AUTH')
)

mycursor = mydb.cursor()
def generateScore(params):
  print(params)

def insertIntoDB(data):
    insertQuery = str(data['latitude']) + ',' + str(data['longitude']) + ',' + str(0)
    mycursor.execute("INSERT INTO LocationTable (Latitude, Longitude, Score ) Values (" + insertQuery + ")")
    mycursor.execute("SELECT LAST_INSERT_ID();")
    locationid = mycursor.fetchone()[0]
    mycursor.execute("INSERT INTO CarTable Values ( " + str(locationid) +", "+ str(data['CarID']) + ",\""+ data['ParkBrake'] + '\",\"' + data['ParkSensor'] + '\",\"' + data['ParkMode']+"\","+ str(data['EngineStart'])+")")
    mycursor.execute("Select * from LocationTable")
    print(mycursor.fetchall())
    mycursor.execute("Select * from CarTable")
    print(mycursor.fetchall())

def getAPIData():
    car_data =  '{ "latitude": 12.911912, "longitude":77.649560, "ParkBrake":"ON", "ParkSensor": "ON","ParkMode": "OFF", "CarID": 53247, "EngineStart": true}'
    return json.loads(car_data)

insertIntoDB(getAPIData())