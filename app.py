
from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime as dt
import os
import json

app = Flask(__name__)

# -------------------
# CONFIG
# -------------------
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDAR_ID = "jlal2inro61imjc30vbkpgnv44@group.calendar.google.com"  # your calendar ID
TOKEN_FILE = "token.json"
API_TOKEN = os.environ.get("API_TOKEN", "Newyorkcity71!")  # set default or use env var


# -------------------
# AUTH CHECK
# -------------------
def check_auth(req):
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    return token == API_TOKEN


# -------------------
# GOOGLE CALENDAR SERVICE
# -------------------
def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("calendar", "v3", credentials=creds)


# -------------------
# ROUTES
# -------------------
@app.route("/list_events", methods=["GET"])
def list_events():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    service = get_service()
    now = dt.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    output = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        output.append({"summary": event["summary"], "start": start})

    return jsonify(output)


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
