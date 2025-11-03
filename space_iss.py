###############################################################
#This is just a starter code for the assignment 1, 
# you need to follow the assignment brief to complete all the tasks required by the assessemnt brief
#
#  This program:
# - Asks the user to enter an access token or use the hard coded access token.
# - Lists the user's Webex rooms.
# - Asks the user which Webex room to monitor for "/seconds" of requests.
# - Monitors the selected Webex Team room every second for "/seconds" messages.
# - Discovers GPS coordinates of the ISS flyover using ISS API.
# - Display the geographical location using geolocation API based on the GPS coordinates.
# - Formats and sends the results back to the Webex Team room.
#
# The student will:
# 1. Import libraries for API requests, JSON formatting, epoch time conversion, and iso3166.
# 2. Complete the if statement to ask the user for the Webex access token.
# 3. Provide the URL to the Webex room API.
# 4. Create a loop to print the type and title of each room.
# 5. Provide the URL to the Webex messages API.
# 6. Provide the URL to the ISS Current Location API.
# 7. Record the ISS GPS coordinates and timestamp.
# 8. Convert the timestamp epoch value to a human readable date and time.
# 9. Provide your Geoloaction API consumer key.
# 10. Provide the URL to the Geoloaction address API.
# 11. Store the location received from the Geoloaction API in a variable.
# 12. Complete the code to format the response message.
# 13. Complete the code to post the message to the Webex room.
###############################################################
 
# 1. Import libraries for API requests, JSON formatting, epoch time conversion, and iso3166.
import requests
import json
import time
from datetime import datetime
from iso3166 import countries
from keys import keys 


# 2. Complete the if statement to ask the user for the Webex access token.
def webexToken():
    choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")
    if choice == "n":
        accessToken = input("please input your access token ")
        accessToken = "Bearer " + accessToken
    else:
        accessToken = "Bearer " + keys.webexKey
# 3. Provide the URL to the Webex room API.
    r = requests.get(   "https://webexapis.com/v1/rooms",
    headers = {"Authorization": accessToken}
    )
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex API. Status code: {}. Text: {}".format(r.status_code, r.text))
        
    return r,accessToken
# 4. Create a loop to print the type and title of each room.
def printRooms(r):
    print("\nList of available rooms:")
    rooms = r.json()["items"]
    for room in rooms:
        print(f"Type: {room['type']} \n Title: {room['title']}")
    roomNameToSearch = input("Which room should be monitored for the /seconds messages? ")
    roomIdToGetMessages = None
    for room in rooms:
        if(room["title"].find(roomNameToSearch) != -1):
            print ("Found rooms with the word " + roomNameToSearch)
            print(room["title"])
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room: " + roomTitleToGetMessages)
        break
    if(roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    return room,roomIdToGetMessages


######################################################################################
# WEBEX BOT CODE
#  Starts Webex bot to listen for and respond to /seconds messages.
######################################################################################
def startBot():
    time.sleep(1)
    GetParameters = {
        "roomId": roomIdToGetMessages,
        "max": 1
    }
    return GetParameters
# 5. Provide the URL to the Webex messages API.    
def Listen(GetParameters,accessToken):
    r = requests.get("https://webexapis.com/v1/messages", 
                         params = GetParameters, 
                         headers = {"Authorization": accessToken}
                    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code ==  200:
        raise Exception( "Incorrect reply from Webex API. Status code: {}. Text: {}".format(r.status_code, r.text))

    json_data = r.json()
    if len(json_data["items"]) == 0:
        print("error, no messages in the room.")    
    messages = json_data["items"]
    message = messages[0]["text"]
    print(message)
    
    if message.find("/") == 0:    
        if (message[1:].isdigit()):
            seconds = int(message[1:])  
        else:
            print("error, message started with a '/' but wasnt followed by numbers, interval set to default 5 seconds")
    else:
        print("error, message must start with a '/' and be followed by numbers, interval set to default 5 seconds")
        seconds = 5
    
    #for the sake of testing, the max number of seconds is set to 5.
        if seconds > 5:
            seconds = 5    
    return seconds    
def iss(seconds):
        time.sleep(seconds)   
# 6. Provide the URL to the ISS Current Location API.         
        r = requests.get("http://api.open-notify.org/iss-now.json")
        json_data = r.json()
        if r.status_code != 200:
            print("error in receiving reply")

# 7. Record the ISS GPS coordinates and timestamp.
        lat = json_data["iss_position"]["latitude"]
        lng = json_data["iss_position"]["longitude"]
        timestamp = json_data["timestamp"]
        
# 8. Convert the timestamp epoch value to a human readable date and time.
        # Use the time.ctime function to convert the timestamp to a human readable date and time.
        timeString = time.ctime(timestamp)      
        return lat,lng,timeString
# 9. Provide your Geoloaction API consumer key.
def geolocation(lat,lng):   
    mapsAPIGetParameters = { 
        "appid":keys.openWeather
                               }
    
# 10. Provide the URL to the Reverse GeoCode API.
    # Get location information using the API reverse geocode service using the HTTP GET method
    r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={keys.openWeather}", 
                             params = mapsAPIGetParameters
                        )

    # Verify if the returned JSON data from the API service are OK
    json_data = r.json()

    if r.status_code != 200:
        print("error, failed to get geolocation data")
# 11. Store the location received from the API in a required variables
    try:
        CountryResult = json_data["sys"]["country"]
        CountryResult = countries.get(CountryResult).name
        try:
            CityResult = json_data["sys"]["name"]
            return CountryResult,CityResult
        except:
            return CountryResult,False  
    except:
        CountryResult = "XZ"
        #Find the country name using ISO3611 country code
        if not CountryResult == "XZ":
            CountryResult = countries.get(CountryResult).name
        return CountryResult,False
# 12. Complete the code to format the response message.
#     Example responseMessage result: In Austin, Texas the ISS will fly over on Thu Jun 18 18:42:36 2020 for 242 seconds.
        #responseMessage = "On {}, the ISS was flying over the following location: \n{} \n{}, {} \n{}\n({}\", {}\")".format(timeString, StreetResult, CityResult, StateResult, CountryResult, lat, lng)
def Spacex():
    launchResponse = requests.get("https://api.spacexdata.com/v4/launches/next")
    launchData = launchResponse.json()
    missionName = launchData["name"]
    launchDate = launchData["date_utc"]
    rocketId = launchData["rocket"]
    launchpadId = launchData["launchpad"]
    rocketResponse = requests.get("https://api.spacexdata.com/v4/rockets/" + rocketId)
    rocketData = rocketResponse.json()
    rocketName = rocketData["name"]
    launchpadResponse = requests.get("https://api.spacexdata.com/v4/launchpads/" + launchpadId)
    launchpadData = launchpadResponse.json()
    launchpadName = launchpadData["name"]
    launchpadLocation = launchpadData["locality"]

    return (launchDate, missionName, rocketName, launchpadName, launchpadLocation)

def finalResult(CountryResult,CityResult,launchDate, missionName, rocketName, launchpadName, launchpadLocation):
        if CountryResult == "XZ":
            responseMessage = "On {}, the ISS was flying over a body of water at latitude {}° and longitude {}°.".format(timeString, lat, lng)
        elif CountryResult and CityResult:
            responseMessage = f"On {timeString}, the ISS was flying over {CityResult} {CountryResult} at a latitude of {lat}° and longitude {lng}°"
        elif CountryResult:
            responseMessage = f"On {timeString}, the ISS was flying over {CountryResult} at a latitude of {lat}° and longitude {lng}°"
        else:
            responseMessage = "error, there has been an error displaying the result"
        # print the response message
        responseMessage = responseMessage + f"\n The next space x launch is on {launchDate} the mission is called {missionName} the rocket is called {rocketName} the launchpad is called {launchpadName} and it is located in {launchpadLocation}"
        print("Sending to Webex: " + responseMessage)

# 13. Complete the code to post the message to the Webex room.         
        # the Webex HTTP headers, including the Authoriztion and Content-Type
        HTTPHeaders = { 
            "Authorization": "Bearer " +keys.webexKey,
            "Content-Type": "application/json"
        }
        
        PostData = {
            "roomId": room["id"],
            "text": responseMessage
        }
        # Post the call to the Webex message API.
        r = requests.post( "https://webexapis.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )
        if r.status_code != 200:
            print("error, there was an error posting to Webex")
        else:
            print("Message successfully sent to Webex.")
                

r,accessToken = webexToken()
room,roomIdToGetMessages = printRooms(r)
getParameters = startBot()
seconds = Listen(getParameters,accessToken)
while True:
    lat,lng,timeString = iss(seconds)
    launchDate, missionName, rocketName, launchpadName, launchpadLocation= Spacex()
    CountryResult,CityResult = geolocation(lat,lng)
    finalResult(CountryResult,CityResult,launchDate, missionName, rocketName, launchpadName, launchpadLocation)
