import csv
from datetime import datetime, timezone
import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def aggregate_data(week, odds_data, score_data):
    games = []
    odds_infos = []
    for odds_game in odds_data:
        logging.debug('Getting event data for game {} at {}'.format(odds_game["away_team"], odds_game["home_team"]))
        events = [event for event in score_data["events"] if event["name"] == (odds_game["away_team"] + " at " + odds_game["home_team"])]
        if len(events) < 1:
            logging.debug('Did not find match for {} at {}'.format(odds_game["away_team"], odds_game["home_team"]))
            continue
        game_info = create_game_info(week, odds_game, events[0])
        odds_info = create_odds_info(week, odds_game)
        games.append(game_info)
        odds_infos.append(odds_info)
    return games, odds_infos


def create_game_info(week, odds_game, score_game):
    date = datetime.strptime(odds_game["commence_time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    address = score_game["competitions"][0]["venue"]["address"]
    game = {
        "week": week,
        "date": date.strftime("%Y-%m-%d"),
        "time": date.strftime("%I:%M %p"),
        "location": address["city"] if "state" not in address else '{}, {}'.format(address["city"], address["state"]),
        "away_team": odds_game["away_team"],
        "home_team": odds_game["home_team"]
    }
    return game


def create_odds_info(week, odds_game):
    h2h_market = get_market(odds_game, "h2h")
    spreads_market = get_market(odds_game, "spreads")
    totals_market = get_market(odds_game, "totals")
    odds_info = {
        "week": week,
        "away_team": odds_game["away_team"],
        "away_team_h2h_price": get_outcome(h2h_market, odds_game["away_team"])["price"],
        "away_team_h2h_bet": False,
        "home_team": odds_game["home_team"],
        "home_team_h2h_price": get_outcome(h2h_market, odds_game["home_team"])["price"],
        "home_team_h2h_bet": False,
        "away_team_spread": get_outcome(spreads_market, odds_game["away_team"])["point"],
        "away_team_spread_price": get_outcome(spreads_market, odds_game["away_team"])["price"],
        "away_team_spread_bet": False,
        "home_team_spread": get_outcome(spreads_market, odds_game["home_team"])["point"],
        "home_team_spread_price": get_outcome(spreads_market, odds_game["home_team"])["price"],
        "home_team_spread_bet": False,
        "over_under": get_outcome(totals_market, "Over")["point"],
        "over_price": get_outcome(totals_market, "Over")["price"],
        "over_bet": False,
        "under_price": get_outcome(totals_market, "Under")["price"],
        "under_bet": False
    }
    return odds_info


def get_market(odds_game, key):
    return [market for market in odds_game["bookmakers"][0]["markets"] if market["key"] == key][0]


def get_outcome(market, name):
    return [outcome for outcome in market["outcomes"] if outcome["name"] == name][0]


def write_csvs(game_data, odds_data, game_filepath, odds_filepath):
    with open(game_filepath, 'w', newline='') as csvfile:
        game_fieldnames = game_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=game_fieldnames)
        writer.writeheader()
        writer.writerows(game_data)
    with open(odds_filepath, 'w', newline='') as csvfile:
        odds_fieldnames = odds_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=odds_fieldnames)
        writer.writeheader()
        writer.writerows(odds_data)


def get_google_api_creds():
    SCOPES = [
        'https://www.googleapis.com/auth/drive'
    ]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def upload_csv_to_google_sheets(creds, sheets_filename, csv_file):
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            "name": sheets_filename,
            "mimeType": 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload(
            csv_file,
            mimetype="text/csv",
            resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id').execute()
    except HttpError as error:
        logging.error('Error while uploading CSV file {} to Google Sheets file {}'.format(csv_file, sheets_filename))
        logging.error(error)
        file = None
    return file.get('id')


def list_google_drive_files(creds):
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
        return
    print('Files:')
    for item in items:
        print(u'{0} ({1})'.format(item['name'], item['id']))