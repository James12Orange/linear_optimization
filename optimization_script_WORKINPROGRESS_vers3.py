# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 20:18:01 2022

@author: jmo5660
"""


from pulp import *
import pandas as pd
import numpy as np

nfl_data=pd.read_csv(r'C:\Users\jmo5660\nfl_data\kubiak2.csv')
nfl_data = nfl_data.loc[nfl_data['Pos.'] != "K"]
nfl_data = nfl_data.loc[nfl_data['Pos.'] != "D"]

risk_numeric = [] 

for x in nfl_data["Risk"]:
    if x == "Green":
        risk_numeric.append(1)
    elif x == "Yellow": 
        risk_numeric.append(2)
    else:
        risk_numeric.append(3)

nfl_data["risk_adjusted"] = risk_numeric

break_out = []
for x in nfl_data["Risk"]:
    if x == "Blue":
        break_out.append(1)
    else:
        break_out.append(0)
        
nfl_data["Break_Out"] = break_out

#print(nfl_data["Overall_Rank"].dtypes)
#print(nfl_data["ESPN ADP_Delta"].dtypes)

espn_draft = []

for x in nfl_data["ESPN ADP_Delta"]:
    if x == '-':
        espn_draft.append(0)
    else:
        espn_draft.append(float(x))

nfl_data["ESPN_Rank"] = espn_draft

nfl_data["Overall_Rank"].astype(int)
nfl_data["ESPN_Rank"].astype(float).astype(int)

nfl_data["Position_Drafted"] = nfl_data["Overall_Rank"] + nfl_data["ESPN_Rank"]
nfl_data["Round_Drafted"] = np.floor(((nfl_data["Position_Drafted"] - 1 )/10) + 1).astype(int)
#nfl_data["Round_Drafted"].astype(str)
nfl_data["FPoints_Over_Baseline"].astype(float).astype(int)

#Get List of Players
players = list(nfl_data["Player"])

#Initialize Dictionaries for Salaries and Positions
draft_delta = dict(zip(players,nfl_data["ESPN_Rank"]))
positions = dict(zip(players,nfl_data["Pos."]))
risk = dict(zip(players,nfl_data["risk_adjusted"]))
break_out_projection = dict(zip(players,nfl_data["Break_Out"]))
round_drafted =  dict(zip(players,nfl_data["Round_Drafted"]))
position_drafted = dict(zip(players,nfl_data["Position_Drafted"]))

#Dictionary for projected score
points_over_base = dict(zip(players, nfl_data["FPoints_Over_Baseline"]))

# Set Players to Take either 1 or 0 values (owned or not)
player_vars = LpVariable.dicts("Player", players, lowBound=0, upBound=1, cat='Integer')


'''
Next we need to setup our problem

The first argument is the name of the problem and the second argument is a parameter 
called sense which can either be set to LpMinimize or LpMaximize. 
We use LpMaximize since we are trying to maximize our projected points.

'''
total_score = LpProblem("Fantasy_Points_Problem", LpMaximize)

#After we have defined the problem, we add our objective function using lpsum():
total_score += lpSum([points_over_base[i] * player_vars[i] for i in player_vars])


#Next, we need to build our constraints
#total_score += lpSum([draft_delta[i] * player_vars[i] for i in player_vars]) <= 50
total_score += lpSum([risk[i] * player_vars[i] for i in player_vars]) <= 28
total_score += lpSum([break_out_projection[i] * player_vars[i] for i in player_vars]) >= 1
total_score += lpSum([break_out_projection[i] * player_vars[i] for i in player_vars]) <= 3


#position constraints
# Get indices of players for each position
qb = [p for p in positions.keys() if positions[p] == 'QB']
rb = [p for p in positions.keys() if positions[p] == 'RB']
wr = [p for p in positions.keys() if positions[p] == 'WR']
te = [p for p in positions.keys() if positions[p] == 'TE']

# Get indices of players for each round
rd1 = [p for p in round_drafted.keys() if round_drafted[p] == 1]
rd2 = [p for p in round_drafted.keys() if round_drafted[p] == 2]
rd3 = [p for p in round_drafted.keys() if round_drafted[p] == 3]
rd4 = [p for p in round_drafted.keys() if round_drafted[p] == 4]
rd5 = [p for p in round_drafted.keys() if round_drafted[p] == 5]
rd6 = [p for p in round_drafted.keys() if round_drafted[p] == 6]
rd7 = [p for p in round_drafted.keys() if round_drafted[p] == 7]
rd8 = [p for p in round_drafted.keys() if round_drafted[p] == 8]
rd9 = [p for p in round_drafted.keys() if round_drafted[p] == 9]
rd10 = [p for p in round_drafted.keys() if round_drafted[p] == 10]
rd11 = [p for p in round_drafted.keys() if round_drafted[p] == 11]
rd12 = [p for p in round_drafted.keys() if round_drafted[p] == 12]
rd13 = [p for p in round_drafted.keys() if round_drafted[p] == 13]
rd14 = [p for p in round_drafted.keys() if round_drafted[p] >= 14]

#set pick
pick1 = [p for p in position_drafted.keys() if position_drafted[p] <= 1]
pick2 = [p for p in position_drafted.keys() if position_drafted[p] <= 2]
pick3 = [p for p in position_drafted.keys() if position_drafted[p] <= 3]
pick4 = [p for p in position_drafted.keys() if position_drafted[p] <= 4]
pick5 = [p for p in position_drafted.keys() if position_drafted[p] <= 5]
pick6 = [p for p in position_drafted.keys() if position_drafted[p] <= 6]
pick7 = [p for p in position_drafted.keys() if position_drafted[p] <= 7]
pick8 = [p for p in position_drafted.keys() if position_drafted[p] <= 8]
pick9 = [p for p in position_drafted.keys() if position_drafted[p] <= 9]
pick10 = [p for p in position_drafted.keys() if position_drafted[p] <= 10]

# Set position Constraints
total_score += lpSum([player_vars[i] for i in qb]) >= 1
total_score += lpSum([player_vars[i] for i in rb]) >= 5
total_score += lpSum([player_vars[i] for i in wr]) >= 5
total_score += lpSum([player_vars[i] for i in te]) >= 1

#Set number of players on roster
total_score += lpSum(player_vars) == 14

# Set round Constraints
total_score += lpSum([player_vars[i] for i in rd1]) == 1
total_score += lpSum([player_vars[i] for i in rd2]) == 1
total_score += lpSum([player_vars[i] for i in rd3]) == 1
total_score += lpSum([player_vars[i] for i in rd4]) == 1
total_score += lpSum([player_vars[i] for i in rd5]) == 1
total_score += lpSum([player_vars[i] for i in rd6]) == 1
total_score += lpSum([player_vars[i] for i in rd7]) == 1
total_score += lpSum([player_vars[i] for i in rd8]) == 1
total_score += lpSum([player_vars[i] for i in rd9]) == 1
total_score += lpSum([player_vars[i] for i in rd10]) == 1
total_score += lpSum([player_vars[i] for i in rd11]) == 1
total_score += lpSum([player_vars[i] for i in rd12]) == 1
total_score += lpSum([player_vars[i] for i in rd13]) == 1
total_score += lpSum([player_vars[i] for i in rd14]) == 1

#set pick constraint
total_score += lpSum([player_vars[i] for i in pick1]) == 0
total_score += lpSum([player_vars[i] for i in pick2]) == 0
total_score += lpSum([player_vars[i] for i in pick3]) == 0
total_score += lpSum([player_vars[i] for i in pick4]) == 0
total_score += lpSum([player_vars[i] for i in pick5]) == 1
total_score += lpSum([player_vars[i] for i in pick6]) == 1
total_score += lpSum([player_vars[i] for i in pick7]) == 1
total_score += lpSum([player_vars[i] for i in pick8]) == 1
total_score += lpSum([player_vars[i] for i in pick9]) == 1
total_score += lpSum([player_vars[i] for i in pick10]) == 1

#Once we have defined the problem, we can solve the problem with one line of code!
total_score.solve()

'''
Once we have done this, our optimized variables are stored in a list by calling total_score.variables(), 
our values for each player are stored in the variable varValue, and the names of our values are stored 
in the name variable of each of the variables. Thus, we can print our lineup by finding the players with 
non-zero values as seen below:
'''

player_list = []

for v in total_score.variables():
    if v.varValue > 0:
        player_list.append(v.name)
        


Optimized_Player_List = pd.DataFrame(player_list)
Optimized_Player_List.rename(columns={0:"Players"}, inplace=True)
Optimized_Player_List['Players'] = Optimized_Player_List['Players'].str.replace('Player', '')
Optimized_Player_List['Players'] = Optimized_Player_List['Players'].str.replace('_', ' ')
Optimized_Player_List['Players'] = Optimized_Player_List['Players'].str.strip()

frames = [Optimized_Player_List, nfl_data]
result = Optimized_Player_List.merge(nfl_data,
                                     left_on=Optimized_Player_List['Players'],
                                     right_on=nfl_data['Player'],
                                     how='left')


print("Current Status: ", LpStatus[total_score.status])
print("Total points: ") 
print(value(total_score.objective))
