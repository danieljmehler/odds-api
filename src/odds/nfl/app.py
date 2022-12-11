import argparse
import json
import logging
import os
import src.odds.api.espn as espn
import src.odds.api.google_sheets as gsheets
import src.odds.api.the_odds_api as odds
import sys
import util

parser = argparse.ArgumentParser(
    prog="NFL Odds API",
    description="Get NFL odds and calculate bet results"
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
    '--game-info-file',
    help="Get basic info about NFL games for a week, like time, date, and location, and write it to the given file as a CSV"
)
parser.add_argument(
    '--odds-info-file',
    help="Get odds info about NFL games for a week, including head-to-head price, spread, and over/under, and write it to the given file as a CSV"
)
parser.add_argument(
    '--create-google-sheet',
    help="Create a Google Sheet for the given local file. If a Google Sheet with the same name already exists, it will be replaced",
    action='append'
)
parser.add_argument(
    '--get-google-sheet-data',
    help="Create a local JSON file from the given Google Sheet. The first row of the Google Sheet is assumed to be a header row."
)
parser.add_argument(
    '--populate-scores',
    help="Update a local JSON file with game scores"
)
parser.add_argument(
    '--populate-bet-results',
    help="Update a local JSON file with bet results"
)
parser.add_argument(
    '--print-results-summary',
    help="Calculate bet results and print a summary"
)

args = parser.parse_args()
logging.basicConfig( level=args.log_level.upper() )

print(args)

creds = gsheets.get_google_api_creds()

if not args.week:
    args.week = espn.get_week()

if args.game_info_file:
    logging.info('Writing game info for week {} to file {}'.format(
        args.week, args.game_info_file))
    espn_data = espn.get_espn_data(args.week)
    game_info_data = util.create_game_info_data(espn_data)
    util.write_csv(game_info_data, args.game_info_file)

if args.odds_info_file:
    logging.info('Writing odds info for week {} to file {}'.format(
        args.week, args.odds_info_file))
    odds_data = odds.get_odds_data(args.week)
    odds_info_data = util.create_odds_info_data(args.week, odds_data)
    util.write_csv(odds_info_data, args.odds_info_file)

if args.create_google_sheet:
    for local_filename in args.create_google_sheet:
        logging.info('Creating Google Sheet of the local file {}'.format(local_filename))
        if not os.path.isfile(local_filename):
            raise FileNotFoundError('File {} does not exist'.format(local_filename))
        gsheet_filename = os.path.basename(local_filename)
        uploaded_file = gsheets.upload_csv(creds, gsheet_filename, local_filename)

if args.populate_scores:
    bet_data = gsheets.get_file_data(creds, args.populate_scores)
    espn_data = espn.get_espn_data(args.week, None, True)
    bet_data = util.add_scores_to_bet_data(bet_data, espn_data)
    with open('output/{}-scores.json'.format(args.populate_scores), 'w') as f:
        json.dump(bet_data, f)