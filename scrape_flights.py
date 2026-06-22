import os
import requests
import json
import config
import smtplib
from email.message import EmailMessage
from datetime import datetime
import gsheets
#from secretload import getCredentials, updateTokenSecret

RUNTIME_DIR = "runtime"
os.makedirs(RUNTIME_DIR, exist_ok=True)

# Function to build and send the email of the price alerts
# Pulls all the parameters from the config file except the main message/body of the email
def sendEmail():
    msg = EmailMessage()
    with open(os.path.join(RUNTIME_DIR, "flight_alert.txt"), "r") as f:
        message = f.read()
        
    if message.strip():     # Check if message/file is empty or not
        msg["From"] = config.FROM_EMAIL
        msg["To"] = config.TO_EMAIL
        msg["Subject"] = config.EMAIL_SUBJECT
        msg.set_content(message)
        
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(config.FROM_EMAIL, config.EMAIL_PASSWORD)
            server.send_message(msg)
        
            print("Email has been sent to " + config.TO_EMAIL)
    else:
        print("File was empty, didn't send email")
    # Clear file once email is sent
    open(os.path.join(RUNTIME_DIR, "flight_alert.txt"), "w").close()


# Mock data used to test features before implementing actual API calls with a key
# Response is the JSON given as example response on rapidapi
def mockAPI():
    with open(os.path.join(RUNTIME_DIR, "search_flights_response.json"), "r") as f:
        data = json.load(f)
    
    return data["data"]["flightOffers"]

# Actual API call, uses BOOKING.COM from Rapidapi.com
def callAPI(querystring):
    response = requests.get(config.SEARCH_FLIGHTS_API_URL, headers=config.HEADERS, params=querystring)

    data = response.json()

    with open(os.path.join(RUNTIME_DIR, "search_flights_response.json"), "w+", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


    return response, data["data"]["flightOffers"]

# Convert the flight departure/arrival time from timestamp to generic time of day for better interpretation in data set
def getTimeOfDay(flightTime: str) -> str:
    dt = datetime.fromisoformat(flightTime)
    hour = dt.hour

    if 4 <= hour < 8:
        return "early morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 16:
        return "afternoon"
    elif 16 <= hour < 20:
        return "evening"
    else:
        return "night"

# Convert the flight duration response from seconds to hours
def getFlightDuration(duration: str) -> str:
    duration_float = float(duration)
    flight_hours = round((duration_float / 3600), 2)

    return str(flight_hours)

# Write specifed data to 'flight_alert.txt'
def flightAlert(data: dict):
    with open(os.path.join(RUNTIME_DIR, "flight_alert.txt"), "a") as file:
        file.write(f"{data["source_airport"]} --> {data["destination_airport"]}, {data["departure_date"]} --> {data["return_date"]}\n"
                   f"{data["airline"]}, Flight Number: {data["flight_code"]}, {data["stops"]} Stops, {data["duration"]} Hours\n"
                   f"{data["class"]}, {data["itinerary_type"]}, {data["total_cost"]} {data["currency"]}\n\n")
                   

# Search through the response data for flight info and prices
def searchFlightOffers(data: dict, departure_date: str, return_date: str):
    day_of_week = datetime.now().strftime('%A')
    with open(os.path.join(RUNTIME_DIR, "flight_data.txt"), "w+") as file:
        for flightOffers in data:
            segments = flightOffers["segments"][0]
            legs = segments["legs"][0]
            # Writes to file in CSV format, can comment out if you don't need it
            file.write(
                f"{legs["carriersData"][0]["name"]},{legs["flightInfo"]["flightNumber"]},{segments["departureAirport"]["cityName"]},{segments["departureAirport"]["code"]},"
                f"{getTimeOfDay(segments["departureTime"])},{(len(segments["legs"])) - 1},{getFlightDuration(segments["totalTime"])},{segments["arrivalAirport"]["cityName"]},"
                f"{segments["arrivalAirport"]["code"]},{getTimeOfDay(segments["arrivalTime"])},{legs["cabinClass"]},{flightOffers["tripType"]},"
                f"{flightOffers["priceBreakdown"]["total"]["currencyCode"]},{flightOffers["priceBreakdown"]["total"]["units"]},{day_of_week},"
                f"{datetime.today().strftime('%Y/%m/%d')},{departure_date},{return_date}\n")
            
            # Saves specified data in a dictionary to then be formatted in the email body if it meets the PRICE_THRESHOLD
            if flightOffers["priceBreakdown"]["total"]["units"] <= config.PRICE_THRESHOLD:
                alert_data = {
                    "airline":legs["carriersData"][0]["name"],
                    "flight_code":legs["flightInfo"]["flightNumber"],
                    "source_airport":segments["departureAirport"]["code"],
                    "stops":(len(segments["legs"])) - 1,
                    "duration":getFlightDuration(segments["totalTime"]),
                    "destination_airport":segments["arrivalAirport"]["code"],
                    "class":legs["cabinClass"],
                    "itinerary_type":flightOffers["tripType"],
                    "total_cost":flightOffers["priceBreakdown"]["total"]["units"],
                    "currency":flightOffers["priceBreakdown"]["total"]["currencyCode"],
                    "departure_date":departure_date,
                    "return_date":return_date
                }
                flightAlert(alert_data)

def main(departure_date: str = config.DEPARTURE_DATE, return_date: str = config.RETURN_DATE):
    departure_date = departure_date
    return_date = return_date

    # API querystring that imports the parameters set in the config.py file
    # -------- IMPORTANT ---------
    # If you left any of the optional parameters in config.py blank such as "child_ages", or if it has a value but you want to omit it
    # then you must comment it out of the querystring dict below.
    querystring = {
        "fromId":config.SOURCE_AIRPORT_CODE,                           # REQUIRED PARAMETER
        "toId":config.DESTINATION_AIRPORT_CODE,                        # REQUIRED PARAMETER
        "departDate":departure_date,                                   # REQUIRED PARAMETER
        "returnDate":return_date,                                      # OPTIONAL
        #"stops":config.STOPS,                                          # OPTIONAL
        "pageNo":config.PAGE_NUMBER,                                   # OPTIONAL
        "adults":config.ADULTS,                                        # OPTIONAL
        #"children":config.CHILDREN,                                    # OPTIONAL
        "sort":config.SORT_ORDER,                                      # OPTIONAL
        "cabinClass":config.CABIN_CLASS,                               # OPTIONAL
        "currency_code":config.CURRENCY_CODE,                          # OPTIONAL
    }

    #mock_data = mockAPI()
    #searchFlightOffers(mock_data)
    # Comment out both lines if not using AWS Secrets Manager
    # getCredentials("Token", "token.json")
    # getCredentials("Credentials", "credentials.json")
    response, data = callAPI(querystring)
    if response.ok:
        searchFlightOffers(data, departure_date, return_date)
        try:
            # Comment out if you don't want Email alerts
            sendEmail()
            # Comment out if you don't want data exported to Google Sheets
            gsheets.main()
            # Comment out if not using AWS Secrets Manager
            # updateTokenSecret("Token", "token.json")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"SearchFlight response returned False with status code: {response.status_code}")
        try:
            error_json = response.json()
            print("Message: ", error_json.get("message", "No message provided."))
        except ValueError:
           print("Raw error: ", response.text)

           
if __name__ == "__main__":
    main()