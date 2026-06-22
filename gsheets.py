import os.path
from dotenv import load_dotenv
#from secretload import getEnvSecret

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
RUNTIME_DIR = "runtime"
os.makedirs(RUNTIME_DIR, exist_ok=True)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
# SAMPLE_SPREADSHEET_ID = getEnvSecret("Env", "SPREADSHEET_ID")
SAMPLE_RANGE_NAME = "Sheet1!A1"

def readText():
  data = []
  with open(os.path.join(RUNTIME_DIR, "flight_data.txt"), "r") as f:
    lines = f.readlines()
    for item in lines:
      data.append(item.split(','))
    f.close()
    return data



def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=3000, prompt="consent", access_type='offline', include_granted_scopes='true')
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    #valueData = [["My"],["First"],["Test"]]
    valueData = readText()
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME, valueInputOption="USER_ENTERED", body={"values": valueData})
        .execute()
    )
    print("Data exported to Google Sheets Successfully")

  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()
  #readText()