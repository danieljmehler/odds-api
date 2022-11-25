import argparse
import util

parser = argparse.ArgumentParser(
    prog="NFL Odds API",
    description="Get NFL odds and calculate bet results"
)
parser.add_argument(
    '-w', '--week',
    help="Week of the NFL season for which to get data. Default is the next upcoming week.",
    default=util.get_week_for_date(),
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
    help="Create a Google Sheet for the given local file. If a Google Sheet with the same name already exists, it will be replaced"
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