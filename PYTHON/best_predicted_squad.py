import pandas as pd
from itertools import combinations
from collections import Counter
import os
import PYTHON.data_cleaning_functions as dcf


def get_best_squad(constraint, rows_to_check=30):
    """
    Get the best predicted FPL squad for the upcoming gameweek, given a constraint.

    :param constraint: {'budget', 'team', 'all', 'none'}
                        What constraints to put on the team.
                        'budget': Get a squad that is within the application budget constraint (£100m)
                        'team': Get a squad within the team constraint, i.e. max 3 players from the same team
                        'all': Have both budget and team constraints on the best squad. Allows you to use team in application.
                        'none': Have no team constraints. Get the squad with the highest predicted points return.
    :param rows_to_check: Number of rows to use in the combinations. Warning the larger the number, the time to return squad gets exponentially larger.
    """
    
    if constraint not in {'budget', 'team', 'all', 'none'}:
        raise ValueError("Constraint variable not within required values: {'budget', 'team', 'all', 'none'}")

    path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/CSV/predictions/'

    predictions = pd.read_csv(path + 'predictions.csv')

    next_fixtures = pd.read_csv(path + 'next_fixtures.csv')
    next_round = max(next_fixtures['round']) + 1

    positions = {'Goalkeepers': (predictions[predictions['position'] == 'GK'], 2),
                 'Defenders': (predictions[(predictions['position'] == 'DEF')], 5),
                 'Midfielders': (predictions[predictions['position'] == 'MID'], 5),
                 'Forwards': (predictions[predictions['position'] == 'FWD'], 3)}

    for position, players in positions.items():
        players_as_lists = [list(row) for i, row in players[0].sort_values(by=['predicted_point_range', 'prob_3', 'prob_2',
                                                                               'prob_1', 'prob_0'], ascending=False)[:rows_to_check].iterrows()]
        positions[position] = combinations(players_as_lists, players[1])

    team_combs = []
    for gks in positions['Goalkeepers']:
        gks_value, gks_points, gks_probs, gks_teams = dcf.sum_of_information(gks)
        for defs in positions['Defenders']:
            defs_value, defs_points, defs_probs, defs_teams = dcf.sum_of_information(defs)
            for mids in positions['Midfielders']:
                mids_value, mids_points, mids_probs, mids_teams = dcf.sum_of_information(mids)
                for fwds in positions['Forwards']:
                    fwds_value, fwds_points, fwds_probs, fwds_teams = dcf.sum_of_information(fwds)
    
                    team_value = sum([gks_value, defs_value, mids_value, fwds_value])
                    team_points = sum([gks_points, defs_points, mids_points, fwds_points])
                    team_probs = sum([gks_probs, defs_probs, mids_probs, fwds_probs])
                    all_teams_counts = Counter(gks_teams + defs_teams + mids_teams + fwds_teams)
    
                    if (constraint == 'all') & (team_value <= 1000) & (max(all_teams_counts.values()) <= 3):
                        team_combs.append([gks, defs, mids, fwds, team_value, team_points, team_probs])
                    elif (constraint == 'team') & (max(all_teams_counts.values()) <= 3):
                        team_combs.append([gks, defs, mids, fwds, team_value, team_points, team_probs])
                    elif (constraint == 'budget') & (team_value <= 1000):
                        team_combs.append([gks, defs, mids, fwds, team_value, team_points, team_probs])
                    elif constraint == 'none':
                        team_combs.append([gks, defs, mids, fwds, team_value, team_points, team_probs])

    if not team_combs:
        print('{} Has No Team Combinations Within Constraint.'.format(constraint))
    else:
        sorted_team_combs = sorted(team_combs, key=lambda x: (x[-2], x[-1]), reverse=True)

        best_squad = []
        for i in range(4):
            player_names = [player for player in [position for position in sorted_team_combs[0][i]]]
            best_squad = best_squad + player_names

        all_starting_combs = combinations(best_squad, 11)

        possible_starting_11s = []
        for team in all_starting_combs:
            positions = [position[2] for position in team]
            position_counts = Counter(positions)
            if position_counts['GK'] == 1:
                if position_counts['DEF'] >= 3:
                    if position_counts['MID'] >= 3:
                        if position_counts['FWD'] >= 1:
                            possible_starting_11s.append([player for player in team])

        possible_starting_11s_stats = []
        for teams in possible_starting_11s:
            team_value, team_points, team_probs, team_teams = dcf.sum_of_information(teams)
            possible_starting_11s_stats.append((team_points, team_probs))

        teams_df = pd.DataFrame(possible_starting_11s)
        teams_df[['Team Points', 'Team Probs']] = possible_starting_11s_stats

        best_starting_11 = list(teams_df.sort_values(by=['Team Points', 'Team Probs'], ascending=False).reset_index().iloc[0, :][:12])[1:]

        subs = dcf.difference_between_lists(best_starting_11, best_squad)

        best_starting_11_df = pd.DataFrame(best_starting_11, columns=predictions.columns)

        subs_df = pd.DataFrame(subs, columns=predictions.columns)
        sub_gk = subs_df.iloc[0, :].copy()
        sub_gk['position'] = 'SubGK'
        out_subs = subs_df.iloc[1:, :].copy()
        out_subs.sort_values(by=['predicted_point_range', 'prob_3', 'prob_2', 'prob_1', 'prob_0'], ascending=False, inplace=True)
        out_subs['position'] = ['Sub1', 'Sub2', 'Sub3']

        fpl_squad = pd.concat([best_starting_11_df, pd.DataFrame(sub_gk).T, out_subs]).set_index('position')

        fpl_squad["captain"] = [1 if prob == max(best_starting_11_df['prob_3']) else 0 for prob in fpl_squad['prob_3']]

        os.mkdir(path + '{}'.format(next_round))
        fpl_squad.to_csv(path + '{rou}/best_squad_{con}.csv'.format(rou=next_round, con=constraint))
