# NFL Odds

Uses [The Odds API](https://the-odds-api.com/) and ESPN data to get NFL game info, odds info, and calculate bet results.

## Usage

### Create the games file for a week

Get NFL games and odds data for a week, and create a Google Sheet with the information:

```script
python3 src/odds/nfl/app.py --week 15 --download-scoreboard-data "output/week15_scoreboard.json" --download-odds-data "output/week15_odds.json" --create-games-file "week15-games"
```

The above command will:

1. Download week 15 scoreboard data (game times, locations, etc.) from ESPN, and save it to the file `output/week15_scoreboard.json`
1. Download week 15 odds data (head-to-head prices, point spreads, and over/unders from FanDuel) from The Odds API, and save it to the file `output/week15_odds.json`
1. Create a CSV file at `output/week15-games.csv` and upload it to Google Sheets with the filename `week15-games`

### Add bets to games file

Go to Google Sheets and open the `week15-games` file.
The Google Sheet has the following columns:

* `week`:  NFL week of the season
* `away_team`:  Away team
* `away_team_h2h_price`: Head-to-head price if betting the away team
* `away_team_h2h_bet`: Bet on the away team to win the game
* `home_team`: Home team
* `home_team_h2h_price`: Head-to-head price if betting the home team
* `home_team_h2h_bet`: Enter a number here for how many dollars you would like to bet on the home team to win the game
* `away_team_spread`: Away team spread
* `away_team_spread_price`: ATS price to bet on the away team to win ATS
* `away_team_spread_bet`: Bet on the away team to win ATS
* `home_team_spread`: Home team spread
* `home_team_spread_price`: ATS price to bet on the home to team to win ATS
* `home_team_spread_bet`: Bet on the home team to win ATS
* `over_under`: Over/under total
* `over_price`: O/U price to bet the over
* `over_bet`: Bet on the over
* `under_price`: O/U price to bet the under
* `under_bet`: Bet on the under

Rename the file `week15-bets`.
Add bets to any or all of the `*_bet` columns to indicate how much you bet on that item.

### Calculate bet results

Calculate bet results for a week:

```script
python3 src/odds/nfl/app.py --week 15 --get-bets-data week15-bets
```