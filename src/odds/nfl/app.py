import argparse
import csv
import json
import logging
import os
import sys

from src.odds.api.EspnApi import EspnApi
from src.odds.api.GoogleSheetsApi import GoogleSheetsApi
from src.odds.api.TheOddsApi import TheOddsApi
from src.odds.nfl.NflWeek import NflWeek

espn_data = None
odds_data = None
nflweek = None
espnapi = EspnApi()
theoddsapi = TheOddsApi()
gsheetsapi = GoogleSheetsApi()
gsheetcred = gsheetsapi.get_google_api_creds()


def get_scoreboard_data(week, filename):
    espn_data = espnapi.get_week_data(week)
    with open(filename, "w") as f:
        json.dump(espn_data, f, indent=4)
    return espn_data


def get_odds_data(week, filename):
    odds_data = theoddsapi.get_odds_data()
    with open(filename, "w") as f:
        json.dump(odds_data, f, indent=4)
    return odds_data


def write_csv(data, filename):
    if os.path.dirname(filename) != '':
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


parser = argparse.ArgumentParser(
    prog="NFL Odds API",
    description="Get NFL odds, make bets, and calculate bet results"
)
parser.add_argument(
    '--log-level',
    help='Provide logging level. Example --log-level debug (default: "warning")',
    default='warning'
)
parser.add_argument(
    '-w', '--week',
    help="Week of the NFL season for which to get data. Default is the next upcoming week.",
    type=int
)
parser.add_argument(
    '--download-odds-data',
    help="Get odds data from The Odds API and save to the given file"
)
parser.add_argument(
    '--download-scoreboard-data',
    help='Get scoreboard data from ESPN and save to the given file'
)
parser.add_argument(
    '--create-games-file',
    help="Get game info and odds for the given week, upload to Google Sheets with the given filename"
)
parser.add_argument(
    '--get-bets-data',
    help="Get bet info from the given Google Sheet filename."
)
parser.add_argument(
    '--calculate-bet-results',
    help="Calculate bet results, summarize, and upload to the given Google Sheet filename"
)

args = parser.parse_args()
logging.basicConfig(level=args.log_level.upper())

week = args.week

if args.download_scoreboard_data:
    espn_data = get_scoreboard_data(week, args.download_scoreboard_data)

if args.download_odds_data:
    odds_data = get_odds_data(week, args.download_odds_data)

if args.create_games_file:
    if espn_data is None:
        espn_data = get_scoreboard_data(
            week, "output/week{}_scoreboard.json".format(week))
    if odds_data is None:
        odds_data = get_odds_data(week, "output/week{}_odds.json".format(week))
    nflweek = NflWeek(week, espn_data=espn_data, odds_data=odds_data)
    csv_data = nflweek.to_csv()
    write_csv(csv_data, "output/{}.csv".format(args.create_games_file))
    gsheetsapi.upload_csv(gsheetcred, args.create_games_file,
                          "output/{}.csv".format(args.create_games_file))

if args.get_bets_data:
    if nflweek is None:
        if espn_data is None:
            espn_data = get_scoreboard_data(
                week, "output/week{}_scoreboard.json".format(week))
        if odds_data is None:
            odds_data = get_odds_data(
                week, "output/week{}_odds.json".format(week))
        nflweek = NflWeek(week, espn_data=espn_data, odds_data=odds_data)
    bet_data = gsheetsapi.get_file_data(gsheetcred, args.get_bets_data, True)[
        "sheets"][0]["rows"]
    print("bet_data={}".format(bet_data))
    nflweek.set_bets(bet_data)
    print(nflweek)

if args.calculate_bet_results:
    if not args.get_bets_data:
        sys.exit('When specifying "--calculate-bet-results" you must also specify "--get-bets-data"')
    


# espn = EspnApi()
# espn_data_week15 = espn.get_week_data(15)
# theoddsapi = TheOddsApi()
# odds_data_week15 = theoddsapi.get_odds_data()
# week15 = NflWeek(week=15, espn_data=espn_data_week15,
#                  odds_data=odds_data_week15)

# with open("output/espn_data_week_15.json", "w") as f:
#     json.dump(espn_data_week15, f)
# with open("output/odds_data_week_15.json", "w") as f:
#     json.dump(odds_data_week15, f)

# print(week15)

# # gsheets = GoogleSheetsApi()
# # creds = gsheets.get_google_api_creds()
# # bet_data = gsheets.get_file_data(
# #     creds, "odds-week14-bets", True)["sheets"][0]["rows"]
