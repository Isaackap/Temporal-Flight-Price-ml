import os
#from secretload import getEnvSecret
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env into environment

# ------------------------------------------------------------- Email Configurations Below ------------------------------------------------------------

# Parameters for sending the email/alert of flight offers.
# The Sender and Receiver email info will be imported from the local .env file as well as the Sender email password (Use app password if 2FA is enabled)
FROM_EMAIL = os.getenv("SENDER_EMAIL")
# FROM_EMAIL = getEnvSecret("Env", "SENDER_EMAIL")
TO_EMAIL = os.getenv("RECEIVER_EMAIL")
# TO_EMAIL = getEnvSecret("Env", "RECEIVER_EMAIL")
EMAIL_PASSWORD = os.getenv("PASSWORD")
# EMAIL_PASSWORD = getEnvSecret("Env", "PASSWORD")
# Parameters for the email server, only variable that needs changing is the 'SMTP_SERVER', adjust it to your sender email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# The subject text of the email, set it to whatever you desire
EMAIL_SUBJECT = "FlightScript Price Alert"


# ------------------------------------------------------------- API Configurations below --------------------------------------------------------------

# The 'url' and 'headers' parameters of the "Search Flights" API request
# These should remain constant, the only value that changes is your personal api key that will be loaded from your local .env file
SEARCH_FLIGHTS_API_URL = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
HEADERS = {
    "x-rapidapi-key": os.getenv("Env", "RAPIDAPI_KEY"),  # Change this to os.getenv() if using that option
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

# This query takes 11 total parameters, some are optional
# Replace the following variables with the data you desire for your flight search, following the correct format

# Set the desired price point to recieve alerts on flight prices
# Make sure the currency matches the set "CURRENCY_CODE" parameter down below
PRICE_THRESHOLD = 1100

# The airport code (usually 3 letters) and the word 'AIRPORT', separated with a '.'
# Example is the George Bush Intercontinental Airport in Houston, TX. Airport code is 'IAH'"
# From/Departure location Id
SOURCE_AIRPORT_CODE = "IAH.AIRPORT"

# To/Arrival location Id, follows same rules as the FROM_ID
DESTINATION_AIRPORT_CODE = "HND.AIRPORT"

# Departure or travel date. Format: YYYY-MM-DD
DEPARTURE_DATE = "2026-10-20"

# Return date. Format: YYYY-MM-DD (optional)
RETURN_DATE = "2026-11-03"

# Filters flights based on the number of stops. Accepted values are: (optional)
# none for no preference (returns flights with any number of stops)
# 0 for non-stop flights
# 1 for one-stop flights
# 2 for two-stop flights
# If provided, the value must be either none, 0, 1, or 2.
STOPS = "0"

# Page number amount, determines how many flight results you get. (optional)
# Returns ~15 flights per page
PAGE_NUMBER = "1"

# The number of guests who are 18 years in age or older. The default value is set to 1 (optional)
ADULTS = "1"

# Pass Children age in the form of string (Ages under 18) Eg: "0,1,17" (optional)
CHILDREN = ""

# Sort by parameter. BEST, CHEAPEST, FASTEST (optional)
SORT_ORDER = "BEST"

# Specifies the preferred cabin class, such as Economy, Premium Economy, Business, or First Class. (optional)
# Available Travel Class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST
CABIN_CLASS = "ECONOMY"

# Sets the currency for price formatting in the response. (optional)
CURRENCY_CODE = "USD"