import mlbstatsapi
from datetime import date
from datetime import datetime
from datetime import timedelta

mlb = mlbstatsapi.Mlb()

# returns schedule for Padres since the beginning of 2025 season to current date based on number of games requested
def getPadresGames(num_games=5):
    schedule = mlb.get_schedule(
        team_id=135,                # Padres team id is 135
        start_date="2025-03-18",    # start of 2025 season
        end_date=str(date.today()),
        game_type='R',
        sport_id=1
    )
    games = [g for g in schedule.dates]
    return [g.games[0].gamepk for g in games[-num_games:]]

# determines is Padres were home/away and returns number of team strikeouts
def getPadresStrikeouts(game_id):
    boxscore = mlb.get_game_box_score(game_id)
    if boxscore.teams.home.team.id == 135:
        padres = boxscore.teams.home
    else:
        padres = boxscore.teams.away
    k = padres.teamstats['pitching']['strikeouts']
    home = boxscore.teams.home.team.name
    away = boxscore.teams.away.team.name
    return [k, home, away]

# returns the date of game from the game_id in clean format
def getPadresGameDate(game_id):
    game = mlb.get_game(game_id)
    game_id = game.gamedata.datetime.originaldate
    game_id = datetime.strptime(game_id,"%Y-%m-%d")
    #game_id = game_id.strftime("%B %d, %Y")
    return game_id


def main():
    #num_games = input("Enter the number of games you wish to look back to: ")
    while True:
        try:
            num_games = int(input("Enter the number of games you wish to look back to: "))
            break
        except ValueError:
            print("Input must be an Integer value.")
            continue
    game_ids = getPadresGames(num_games)    # searching for strikeouts in Padres most recent game
    for game_id in game_ids:
        k, home, away = getPadresStrikeouts(game_id)
        game_date = getPadresGameDate(game_id)
        purchase_date = game_date   # discount applies for next day after the game
        game_date = game_date.strftime("%B %d, %Y")
        print(f"{game_date} - {away} at {home}: Padres score {k} strikeouts")
        if k >= 9:
            purchase_date = purchase_date + timedelta(days=1)
            purchase_date = purchase_date.strftime("%B %d, %Y")
            print(f"Petco will have 25% for all of {purchase_date}!")
        else:
            print("No Petco discount.")


if __name__ == "__main__":
    main()