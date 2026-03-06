import mlbstatsapi
from datetime import date, datetime, timedelta, timezone

mlb = mlbstatsapi.Mlb()

### returns recent schedule of games for Padres since the beginning of 
### 2025 season to current date based on number of games requested
def getPadresGames(num_games=5):
    schedule = mlb.get_schedule(
        team_id=135,                # Padres team id is 135
        start_date='2025-03-18',    # start of 2025 season
        end_date=str(date.today()),
        game_type='R',
        sport_id=1
    )
    games = [g for g in schedule.dates]

    # check if most recent game on schedule has happened yet or not,
    # if not remove from list and start with the game before it
    game_time = games[-1].games[0].game_date
    game_time = datetime.fromisoformat(game_time)
    if game_time > datetime.now(timezone.utc): # most recently scheduled game hasn't started
        del games[-1]
    games = games[-num_games:]
    return games


### determines if Padres were home/away and returns number of team strikeouts
### returns padres strikeouts, and the team names
def getPadresStrikeouts(game_id):
    boxscore = mlb.get_game_box_score(game_id)
    if boxscore.teams.home.team.id == 135: # padres team id
        padres = boxscore.teams.home
    else:
        padres = boxscore.teams.away
    k = padres.team_stats['pitching']['strikeOuts']
    home = boxscore.teams.home.team.name
    away = boxscore.teams.away.team.name
    return [k, home, away]


### handles user input for number of games to look at
### returns number of games as an integer
def userInput():
    while True:
        try:
            num_games = int(input('Enter the number of games you wish to look back to: '))
            break
        except ValueError:
            print('Input must be an Integer value.')
            continue
    return num_games


### handles continuation of program calling for different number of games
def userContinue():
    while True:
        user_continue = input('Would you like to check a different number of games? (y/n): ')
        if user_continue.lower() == 'y':
            num_games = userInput()
            checkDiscount(num_games)
        elif user_continue.lower() == 'n':
            print('Thank you! Good day')
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
            continue


### main calculation of availability of Petco discount
def checkDiscount(num_games):
    games = getPadresGames(num_games)    # searching for strikeouts in Padres most recent game
    for n in range(num_games):
        game_id = games[n].games[0].game_pk # game_pk same as game_id
        game_date = games[n].games[0].game_date
        game_date = datetime.fromisoformat(game_date)
        purchase_date = game_date + timedelta(days=1)

        k, home, away = getPadresStrikeouts(game_id)
        print(f'{game_date.date()} - {away} at {home}: \nPadres score {k} strikeouts', end=" | ") 
        if k >= 9:
            purchase_date = purchase_date.strftime("%B %d, %Y")
            print(f'Petco will have 25% for all of {purchase_date}!\n')
        else:
            print('No Petco discount.\n')


def main():
    num_games = userInput()
    checkDiscount(num_games)
    userContinue()


if __name__ == '__main__':
    main()
