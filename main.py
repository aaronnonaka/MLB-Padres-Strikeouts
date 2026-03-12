import mlbstatsapi
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import streamlit as st

# initialize session states and others
if 'beginning_date' not in st.session_state:
    st.session_state.beginning_date = '2025-03-18' # start of 2025 season
    # change to start of 2026 season, 2026-03-26
if 'end_date' not in st.session_state:
    st.session_state.end_date = str(date.today())


mlb = mlbstatsapi.Mlb()

### returns recent schedule of games for Padres since the beginning of 
### 2025 season to current date based on number of games requested
def getPadresGames(num_games=5):
    schedule = mlb.get_schedule(
        team_id=135,                # Padres team id is 135
        start_date=st.session_state.beginning_date,    # start of 2025 season, default
        end_date=st.session_state.end_date,        # current date
        game_type='R',
        sport_id=1
    )
    if schedule == None:
        return None
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

### main calculation of availability of Petco discount
def checkDiscount(num_games):
    games = getPadresGames(num_games)    # searching for strikeouts in Padres most recent game
    if games == None:
        st.markdown('No games found in this time frame.')
        return
    # schedule of games returned not as many as user request
    if len(games) < num_games:
        st.markdown(f'**Only {len(games)} games found for the Padres in that time frame.**')
        num_games = len(games)
    for n in range(num_games):
        game_id = games[n].games[0].game_pk # game_pk same as game_id
        game_date = games[n].games[0].game_date
        game_date = datetime.fromisoformat(game_date)
        local_date = game_date.astimezone(ZoneInfo('America/Los_Angeles'))
        purchase_date = game_date + timedelta(days=1)

        k, home, away = getPadresStrikeouts(game_id)
        st.session_state.results.markdown(
            f'{local_date.date()} - {away} at {home}: Padres scored **{k}** strikeouts.')
        if k >= 9:
            print_purchase_date = purchase_date.strftime("%B %d, %Y")
            if purchase_date.date() == date.today():
                st.session_state.results.write(
                    f'Petco will have a 25% discount for all of today, {print_purchase_date}!')
            else:
                st.session_state.results.write(
                    f'Petco had a 25% discount on {print_purchase_date}.')
        else:
            st.session_state.results.write('Not enough strikeouts, no K-9 Petco discount.')
        st.session_state.results.divider()

### get beginning and end dates for search, has default parameters
def getDates():
    col1, col2 = st.columns(2, vertical_alignment='bottom')
    with col1:
        st.date_input('Beginning date of search (default is start of 2025 season, 03/18/2025):', 
                    key='beginning_date',
                    format='MM/DD/YYYY',
                    min_value = date(2025, 3, 18),
                    max_value = st.session_state.end_date)
    with col2:
        st.date_input(f'End date of search (default is current date, {date.today().strftime("%m/%d/%Y")}):',
                    key='end_date',
                    format='MM/DD/YYYY',
                    min_value = st.session_state.beginning_date,
                    max_value = date.today())

### check future scheduled games for Padres
def checkSchedule(num_sched):
    schedule = mlb.get_schedule(
        team_id=135,                # Padres team id is 135
        start_date=date.today(),    # start of 2025 season, default
        end_date='2026-09-27',      # last game of 2026 season
        game_type='R',
        sport_id=1
    )
    if schedule == None:
        st.markdown('No games found in this time frame.')
        return
    games = [g for g in schedule.dates]
    if len(games) < num_sched:
        st.markdown(f'**Only {len(games)} games found scheduled for the Padres through the 2026 season.**')
        num_sched = len(games)
    for n in range(num_sched):
        game_id = games[n].games[0].game_pk # game_pk same as game_id
        game_date = games[n].games[0].game_date
        game_date = datetime.fromisoformat(game_date) # date is UTC, convert to local time for display
        local_date = game_date.astimezone(ZoneInfo('America/Los_Angeles'))

        k, home, away = getPadresStrikeouts(game_id)
        st.session_state.sched.markdown(
            f'{local_date.date()} - {away} at {home}.')
    
### code in streamlit web app
def main():
    st.set_page_config(page_title='Padres Strikeout Application', page_icon='⚾', layout='centered')
    st.html("""
    <style>
        .stMainBlockContainer {
            max-width:60rem;
        }
    </style>
    """)
    st.title('Padres Strikeout and Petco Discount Checker')
    st.write('Determine if Petco will have a store-wide discount based on the Padres strikeout performance.')    
    st.write('Petco offers a 25% discount the day after the Padres score 9 or more strikeouts in their game.')
    
    ### function for setting beginning and end dates for search parameters
    getDates()

    ### function for searching games, getting strikeouts, and displaying results
    st.number_input('Enter the number of games you wish to look back to:', step=1, key='num_games')
    if st.session_state.num_games:
        st.write(f'Checking Padres last {st.session_state.num_games} games for strikeout data...')
        st.session_state.results = st.expander('Results')
        checkDiscount(int(st.session_state.num_games))

    ### function for searching for next scheduled game
    st.markdown('#')
    st.header('Check the schedule for upcoming games.')
    st.number_input('Enter the number of games you wish to search ahead for:', step=1,key='num_sched')
    if st.session_state.num_sched:
        st.write(f'Checking for the Padres next {st.session_state.num_sched} scheduled games...')
        st.session_state.sched = st.expander('Scheduled Games')
        checkSchedule(int(st.session_state.num_sched))


if __name__ == '__main__':
    main()
