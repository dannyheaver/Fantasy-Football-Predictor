from pandas.io import sql
import pandas as pd
from datetime import timedelta


def minutes_played(dataframe):
    """
    Removes all players that didn't play a single minute in each observation.

    :param dataframe: A gameweeks dataframe.
    :return: The gameweeks dataframe containing observations
    """
    return dataframe[dataframe['minutes'] > 0]


def add_season(season, dataframe):
    """
    Add a column to a dataframe, where every value is a string of the season that it represents.

    :param season: A string of the season of the dataframe.
    :param dataframe: A gameweeks dataframe.
    """
    dataframe.insert(0, 'season', season)


def gameweeks_name_cleaner(dataframe):
    """
    Replace underscores and numbers for spaces in the player names to make them consistent across all seasons.

    :param dataframe: A gameweeks dataframe.
    """
    dataframe['name'] = [name[0] + ' ' + name[1] for name in [string.split(sep='_') for string in dataframe['name']]]


def positions_name_cleaner(dataframe):
    """
    Join a players first and second name in a positions dataframe.

    :param dataframe: A positions dataframe.
    """
    dataframe['player_name'] = [name[0] + ' ' + name[1] for name in zip(dataframe['first_name'],
                                                                        dataframe['second_name'])]


def to_sql(dataframe, season, connection, dataframe_type):
    """
    Creates a table in an SQL database from a dataframe.

    :param dataframe: The dataframe you want to make into a table in the database.
    :param season: The season of the dataframe.
    :param connection: The connection to the SQL database.
    :param dataframe_type: {'positions', 'gameweeks', 'odds', 'defenders}
                           What type of dataframe we are making into a table.
    """
    dataframe.to_sql(name='{type}_{season}'.format(type=dataframe_type, season=season), con=connection,
                     if_exists='replace', index=False)


def position_joiner_and_cleaner(gameweeks_dataframe, positions_dataframe, season, connection):
    """
    Joins the positions of every player from the positions dataframes onto the gameweeks dataframes.

    :param gameweeks_dataframe: A gameweeks dataframe.
    :param positions_dataframe: The corresponding positions dataframe.
    :param season: {'2016-17', '2017-18', '2018-19', '2019-20'}
                   The specified season that you will be joining the positions on.
    :param connection: The connection to the SQL database.
    :return: The gameweeks dataframe with cleaned positions appended to each observation.
    """
    to_sql(gameweeks_dataframe, season, connection, 'gameweeks')
    to_sql(positions_dataframe, season, connection, 'positions')

    sql_string = '''
                 SELECT a.*, b.element_type
                 FROM gameweeks_{season} a
                 LEFT JOIN positions_{season} b
                 ON a.name = b.player_name
                 '''
    dataframe = sql.read_sql(sql_string.format(season=season), con=connection)
    dataframe['element_type'] = dataframe['element_type'].replace({1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'})
    dataframe.rename(columns={'element_type': 'position'}, inplace=True)
    return dataframe


def clean_team_names(gameweeks_dataframe, odds_dataframe):
    """
    Changes the opponents team from integers to strings of the team names.

    :param gameweeks_dataframe: The dataframe you want to transform.
    :param odds_dataframe: The dataframe with the team names as strings.
    """
    gameweeks_dataframe['opponent_team'] = gameweeks_dataframe['opponent_team'].replace(
        {key + 1: value for key, value in enumerate(sorted(odds_dataframe['HomeTeam'].unique()))})


def home_and_away_teams(dataframe):
    """
    Gets the home and away teams for each gameweeks observation.

    :param dataframe: The gameweeks dataframe.
    """
    fixture_ids = {}
    for i in range(1, max(dataframe['fixture'] + 1)):
        fixture_ids[i] = set(dataframe[dataframe['fixture'] == i]['opponent_team'])

    dataframe['home_team'] = [[team for team in fixture_ids[fixture] if team != opponent][0] if is_home else opponent
                              for is_home, opponent, fixture in
                              zip(dataframe['was_home'], dataframe['opponent_team'], dataframe['fixture'])]
    dataframe['away_team'] = [opponent if is_home else [team for team in fixture_ids[fixture] if team != opponent][0]
                              for is_home, opponent, fixture in
                              zip(dataframe['was_home'], dataframe['opponent_team'], dataframe['fixture'])]


def played_for(dataframe):
    """
    Get the team that each player plays for in each observation.

    :param dataframe: The gameweeks dataframe.
    """
    dataframe['plays_for'] = [home if is_home else away for is_home, home, away in
                              zip(dataframe['was_home'], dataframe['home_team'], dataframe['away_team'])]


def odds_joiner(gameweeks_dataframe, odds_dataframe, season, connection):
    """
    Joins the odds of each fixture onto each player observation in the gameweeks dataframe.

    :param gameweeks_dataframe: A gameweeks dataframe.
    :param odds_dataframe: The corresponding odds dataframe.
    :param season: {'2016-17', '2017-18', '2018-19', '2019-20'}
                   The specified season that you will be joining the positions on.
    :param connection: The connection to the SQL database.
    :return: The gameweeks dataframe with the bookies odds appended to each observation.
    """
    to_sql(gameweeks_dataframe, season, connection, 'gameweeks')
    to_sql(odds_dataframe, season, connection, 'odds')

    sql_string = '''
                 SELECT *
                 FROM gameweeks_{season} a
                 LEFT JOIN odds_{season} b
                 ON a.home_team = b.HomeTeam AND a.away_team = b.AwayTeam
                 '''
    return sql.read_sql(sql_string.format(season=season), con=connection)


def dates_cleaner(dataframe):
    """
    Adds the month and time of the match as categorical columns.

    :param dataframe: A gameweeks dataframe.
    """
    dataframe['kickoff_time'] = pd.to_datetime(dataframe['kickoff_time'])
    dataframe['date_of_match'] = dataframe['kickoff_time'].dt.date
    dataframe['month_of_match'] = dataframe['kickoff_time'].dt.month
    dataframe['time_of_match'] = [str(time)[:5] for time in (dataframe['kickoff_time'] + timedelta(hours=1)).dt.time]


def win_expectation(dataframe, type_to_add):
    """
    Gets the ratio of the probability of the players team winning the match from the bookies odds.

    :param dataframe: A gameweeks dataframe.
    :param type_to_add: {'normal', 'shift'}
                 Whether to make the win expectation for the current game or the shifted game.
    """
    if type_to_add == 'normal':
        dataframe['win_expectation'] = [avgA / avgH if home else avgH / avgA for home, avgH, avgA in
                                        zip(dataframe['was_home'], dataframe['B365H'], dataframe['B365A'])]
    elif type_to_add == 'shift':
        dataframe['shift_win_expectation'] = [avgA / avgH if home else avgH / avgA for home, avgH, avgA in
                                              zip(dataframe['shift_was_home'], dataframe['B365H'], dataframe['B365A'])]
    else:
        raise ValueError('type not in specified values')


def adjust_points(dataframe):
    """
    Removes points players earn for minutes played. Adjusted points are therefore performance based only.

    :param dataframe: A gameweeks dataframe.
    """
    dataframe['adjusted_points'] = [points - 1 if minutes < 60 else points - 2 for minutes, points in
                                    zip(dataframe['minutes'], dataframe['total_points'])]


def won_the_game(dataframe):
    """
    Binary value on whether the players team won the match.

    :param dataframe: A gameweeks dataframe.
    """
    home_away = ['H' if was_home else 'A' for was_home in list(dataframe['was_home'])]

    dataframe['won'] = [0 if won == 'D' else 1 if homeaway == won else -1 for homeaway, won in
                        zip(home_away, dataframe['FTR'])]


def mean_statistics(dataframe):
    """
    Gets the rolling mean of the players statistics from their previous 3 appearances.

    :param dataframe: A gameweeks dataframe.
    """
    dataframe.sort_values(by='date_of_match', ascending=False, inplace=True)
    mean_points, mean_creativity, mean_threat, mean_influence, mean_bps, mean_goals, mean_assists, mean_conceded \
        = ([] for _ in range(8))
    for player, date in zip(dataframe['name'], dataframe['date_of_match']):
        players_df = dataframe[(dataframe['name'] == player) & (dataframe['date_of_match'] < date)][:3]
        mean_points.append(players_df['adjusted_points'].mean())
        mean_creativity.append(players_df['creativity'].mean())
        mean_threat.append(players_df['threat'].mean())
        mean_influence.append(players_df['influence'].mean())
        mean_bps.append(players_df['bps'].mean())
        mean_goals.append(players_df['goals_scored'].mean())
        mean_assists.append(players_df['assists'].mean())
        mean_conceded.append(players_df['goals_conceded'].mean())
    dataframe['mean_points'] = mean_points
    dataframe['mean_creativity'] = mean_creativity
    dataframe['mean_threat'] = mean_threat
    dataframe['mean_influence'] = mean_influence
    dataframe['mean_bps'] = mean_bps
    dataframe['mean_goals'] = mean_goals
    dataframe['mean_assists'] = mean_assists
    dataframe['mean_conceded'] = mean_conceded
    dataframe['mean_points'].fillna(dataframe['adjusted_points'], inplace=True)
    dataframe['mean_creativity'].fillna(dataframe['creativity'], inplace=True)
    dataframe['mean_threat'].fillna(dataframe['threat'], inplace=True)
    dataframe['mean_influence'].fillna(dataframe['influence'], inplace=True)
    dataframe['mean_bps'].fillna(dataframe['bps'], inplace=True)
    dataframe['mean_goals'].fillna(dataframe['goals_scored'], inplace=True)
    dataframe['mean_assists'].fillna(dataframe['assists'], inplace=True)
    dataframe['mean_conceded'].fillna(dataframe['goals_conceded'], inplace=True)


def shift_match_info(dataframe):
    """
    Shifts the match information and rolling mean statistics so we can use this information to predict the next games
    points return.

    :param dataframe: A gameweeks dataframe.
    """
    shift_points, shift_opponent, shift_we, shift_mom, shift_tom, shift_home, shift_mean_points, \
    shift_mean_creativity, shift_mean_threat, shift_mean_influence, shift_mean_bps, shift_mean_goals, \
    shift_mean_assists, shift_mean_conceded = ([] for _ in range(14))
    for player in dataframe['name'].unique():
        players_df = dataframe[dataframe['name'] == player].sort_values(by='date_of_match', ascending=False)
        shift_points.append(players_df['adjusted_points'].shift())
        shift_opponent.append(players_df['opponent_team'].shift())
        shift_we.append(players_df['win_expectation'].shift())
        shift_mom.append(players_df['month_of_match'].shift())
        shift_tom.append(players_df['time_of_match'].shift())
        shift_home.append(players_df['was_home'].shift())
        shift_mean_points.append(players_df['mean_points'].shift())
        shift_mean_creativity.append(players_df['mean_creativity'].shift())
        shift_mean_threat.append(players_df['mean_threat'].shift())
        shift_mean_influence.append(players_df['mean_influence'].shift())
        shift_mean_bps.append(players_df['mean_bps'].shift())
        shift_mean_goals.append(players_df['mean_goals'].shift())
        shift_mean_assists.append(players_df['mean_assists'].shift())
        shift_mean_conceded.append(players_df['mean_conceded'].shift())
    dataframe['shift_points'] = pd.concat(shift_points).sort_index()
    dataframe['shift_opponent'] = pd.concat(shift_opponent).sort_index()
    dataframe['shift_win_expectation'] = pd.concat(shift_we).sort_index()
    dataframe['shift_month_of_match'] = pd.concat(shift_mom).sort_index()
    dataframe['shift_time_of_match'] = pd.concat(shift_tom).sort_index()
    dataframe['shift_was_home'] = pd.concat(shift_home).sort_index()
    dataframe['shift_mean_points'] = pd.concat(shift_mean_points).sort_index()
    dataframe['shift_mean_creativity'] = pd.concat(shift_mean_creativity).sort_index()
    dataframe['shift_mean_threat'] = pd.concat(shift_mean_threat).sort_index()
    dataframe['shift_mean_influence'] = pd.concat(shift_mean_influence).sort_index()
    dataframe['shift_mean_bps'] = pd.concat(shift_mean_bps).sort_index()
    dataframe['shift_mean_goals'] = pd.concat(shift_mean_goals).sort_index()
    dataframe['shift_mean_assists'] = pd.concat(shift_mean_assists).sort_index()
    dataframe['shift_mean_conceded'] = pd.concat(shift_mean_conceded).sort_index()


def useful_columns(dataframe):
    """
    Only returns the columns we will be using in modeling in each dataframe.

    :param dataframe: A gameweeks dataframe.
    """
    columns = ['season', 'name', 'position', 'value', 'adjusted_points', 'assists', 'goals_scored', 'goals_conceded',
               'saves', 'own_goals', 'penalties_missed', 'penalties_saved', 'clean_sheets', 'creativity', 'threat',
               'influence', 'bps', 'minutes', 'yellow_cards', 'red_cards', 'plays_for', 'opponent_team', 'was_home',
               'won', 'month_of_match', 'time_of_match', 'win_expectation', 'mean_points', 'mean_creativity',
               'mean_threat', 'mean_influence', 'mean_bps', 'mean_goals', 'mean_assists', 'mean_conceded',
               'shift_opponent', 'shift_win_expectation', 'shift_month_of_match', 'shift_time_of_match',
               'shift_was_home', 'shift_mean_points', 'shift_mean_creativity', 'shift_mean_threat',
               'shift_mean_influence', 'shift_mean_bps', 'shift_mean_goals', 'shift_mean_assists',
               'shift_mean_conceded', 'round', 'date_of_match']
    try:
        return dataframe[columns + ['shift_points']]
    except KeyError:
        return dataframe[columns]


def attacking_or_defending(dataframe, connection):
    """
    Splits the defenders into attacking (full backs) or defending (centre backs) defenders depending on the players
    median creativity in the season. Can only be done on the concatenated gameweeks dataframe otherwise large number
    of errors in positions.

    :param dataframe: The concatenated gameweeks dataframe.
    :param connection: The connection to the SQL database.
    :return:
    """
    defenders = dataframe[(dataframe['position'] == 'DEF')].groupby(['name']).median().reset_index()
    defenders['type_of_def'] = ['AttDEF' if creativity > 2 else 'DefDEF' for creativity in defenders['creativity']]

    to_sql(defenders, 'all', connection, 'defenders')
    to_sql(dataframe, 'all', connection, 'gameweeks')

    sql_string = '''
                 SELECT a.*, b.type_of_def
                 FROM gameweeks_all a
                 LEFT JOIN defenders_all b
                 ON a.name = b.name
                 '''

    dataframe = sql.read_sql(sql_string, con=connection)

    dataframe['position'] = [defpos if position == 'DEF' else position for position, defpos in
                             zip(dataframe['position'], dataframe['type_of_def'])]

    dataframe.drop('type_of_def', axis=1, inplace=True)
    return dataframe


def form_against_next_opponent(fixtures_dataframe, gameweeks_dataframe):
    """
    Gets the mean statistics for a player against the specified shifted opponent.

    :param fixtures_dataframe: The dataframe you want to add the form to.
    :param gameweeks_dataframe: The dataframe with the players names you want to sort through.
    """
    points_ano, creativity_ano, threat_ano, influence_ano, bps_ano, goals_ano, assists_ano, conceded_ano = \
        ([] for _ in range(8))
    for player, opponent in zip(fixtures_dataframe['name'], fixtures_dataframe['shift_opponent']):
        players_df = gameweeks_dataframe[(gameweeks_dataframe['name'] == player) & (gameweeks_dataframe['opponent_team']
                                                                                    == opponent)]
        points_ano.append(players_df['adjusted_points'].mean())
        creativity_ano.append(players_df['creativity'].mean())
        threat_ano.append(players_df['threat'].mean())
        influence_ano.append(players_df['influence'].mean())
        bps_ano.append(players_df['bps'].mean())
        goals_ano.append(players_df['goals_scored'].mean())
        assists_ano.append(players_df['assists'].mean())
        conceded_ano.append(players_df['goals_conceded'].mean())
    fixtures_dataframe['points_against_shift_opponent'] = points_ano
    fixtures_dataframe['creativity_against_shift_opponent'] = creativity_ano
    fixtures_dataframe['threat_against_shift_opponent'] = threat_ano
    fixtures_dataframe['influence_against_shift_opponent'] = influence_ano
    fixtures_dataframe['bps_against_shift_opponent'] = bps_ano
    fixtures_dataframe['goals_against_shift_opponent'] = goals_ano
    fixtures_dataframe['assists_against_shift_opponent'] = assists_ano
    fixtures_dataframe['conceded_against_shift_opponent'] = conceded_ano


def shifted_points_range(dataframe):
    """
    Turns the shifted points into a categorical value.

    :param dataframe: The concatenated gameweeks dataframe.
    """
    shift_points = dataframe['shift_points']
    dataframe['shift_points_range'] = pd.cut(shift_points,
                                             [min(shift_points.dropna()), 0, 4, 10, max(shift_points.dropna())],
                                             labels=[0, 1, 2, 3])
    dataframe.drop('shift_points', axis=1, inplace=True)


def next_odds_joiner(fixtures_dataframe, odds_dataframe, connection):
    """
    Joins the odds of each upcoming fixture onto each player observation in the gameweeks dataframe.

    :param fixtures_dataframe: The dataframe of the upcoming fixtures.
    :param odds_dataframe: The dataframe with the next odds in it.
    :param connection: The connection to the SQL database.
    :return: The next_fixtures dataframe with the next odds appended to it.
    """
    to_sql(fixtures_dataframe, 'fixtures', connection, 'next')
    to_sql(odds_dataframe, 'odds', connection, 'next')
    sql_string = '''
                 SELECT *
                 FROM next_fixtures a
                 LEFT JOIN next_odds b
                 ON a.plays_for = b.shift_home_team OR a.plays_for = b.shift_away_team
                 '''
    return sql.read_sql(sql_string, con=connection)


def shifted_was_home(dataframe):
    """
    See if the players upcoming game is at home or away.

    :param dataframe: The next fixtures dataframe.
    """
    dataframe['shift_was_home'] = [1 if home == team else 0 for home, team in
                                   zip(dataframe['shift_home_team'], dataframe['plays_for'])]


def shifted_opponent(dataframe):
    """
    Get the shifted opponent.

    :param dataframe: The next fixtures dataframe.
    """
    dataframe['shift_opponent'] = [away if was_home else home for was_home, home, away in
                                   zip(dataframe['shift_was_home'], dataframe['shift_home_team'],
                                       dataframe['shift_away_team'])]


def shift_match_stats_for_next_fixtures(fixtures_dataframe, gameweeks_dataframe):
    """
    Get the mean match stats for the final played gameweek.

    :param fixtures_dataframe: The fixtures dataframe.
    :param gameweeks_dataframe: The gameweeks dataframe.
    """
    mean_points, mean_creativity, mean_threat, mean_influence, mean_bps, mean_goals, mean_assists, mean_conceded = ([] for _ in range(8))
    for player in fixtures_dataframe['name']:
        players_df = gameweeks_dataframe[(gameweeks_dataframe['name'] == player)].sort_values(by='date_of_match',
                                                                                              ascending=False)[:3]
        mean_points.append(players_df['adjusted_points'].mean())
        mean_creativity.append(players_df['creativity'].mean())
        mean_threat.append(players_df['threat'].mean())
        mean_influence.append(players_df['influence'].mean())
        mean_bps.append(players_df['bps'].mean())
        mean_goals.append(players_df['goals_scored'].mean())
        mean_assists.append(players_df['assists'].mean())
        mean_conceded.append(players_df['goals_conceded'].mean())
    fixtures_dataframe['shift_mean_points'] = mean_points
    fixtures_dataframe['shift_mean_creativity'] = mean_creativity
    fixtures_dataframe['shift_mean_threat'] = mean_threat
    fixtures_dataframe['shift_mean_influence'] = mean_influence
    fixtures_dataframe['shift_mean_bps'] = mean_bps
    fixtures_dataframe['shift_mean_goals'] = mean_goals
    fixtures_dataframe['shift_mean_assists'] = mean_assists
    fixtures_dataframe['shift_mean_conceded'] = mean_conceded


def fill_null_shift_opponent(dataframe):
    """
    Fills the null values in the mean statistics against the shifted opponent with the mean values from the last 3
    games.

    :param dataframe: The next_fixtures dataframe.
    """
    opponent_columns = ['points_against_shift_opponent', 'creativity_against_shift_opponent',
                        'threat_against_shift_opponent', 'influence_against_shift_opponent',
                        'bps_against_shift_opponent', 'goals_against_shift_opponent',
                        'assists_against_shift_opponent', 'conceded_against_shift_opponent']
    mean_columns = ['mean_points', 'mean_creativity', 'mean_threat', 'mean_influence', 'mean_bps', 'mean_goals',
                    'mean_assists', 'mean_conceded']
    for column1, column2 in zip(opponent_columns, mean_columns):
        dataframe[column1].fillna(dataframe[column2], inplace=True)


def sum_of_information(list_of_players):
    """
    Sum of players stats for the combinations of players in that position, as well as a list of the teams.

    :param list_of_players: List of player combinations in a specified position.
    :return: (sum_of_values, sum_of_predicted_points, sum_of_probability_of_3, list_of_teams)
    """
    values = sum([player[1] for player in list_of_players])
    points = sum([player[5] for player in list_of_players])
    probs_3 = sum([player[9] for player in list_of_players])
    teams = [player[3] for player in list_of_players]
    return values, points, probs_3, teams


def difference_between_lists(list1, list2):
    """
    A function that returns the difference between two lists.

    :param list1: List of elements
    :param list2: List of elements
    :return: A list of elements that are in one list and not in the other.
    """
    return [i for i in list1 + list2 if i not in list1 or i not in list2]


def fix_columns(data, columns):
    """
    A function that adds columns of 0 to a dataframe in the case that a test set did not contain all the categorical
    values that were in the training set. It then asserts the dataframe to make sure it has all the columns needed for
    modeling.

    :param data: The dataframe we are going to transform
    :param columns: The columns we want in the transformed dataframe
    :return: The transformed dataframe with the columns equal to the columns input.
    """
    missing_columns = set(columns) - set(data.columns)
    for column in missing_columns:
        data[column] = 0
    return data[columns]