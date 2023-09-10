import random

def draft_balancer(list_mmr):
    team_order1 = ['', '', '', '', '', '', '', '', '', '']
    radiant1 = 0
    dire1 = 0
    for n in range(0, 10, 2):
        if radiant1 == dire1 or radiant1 < dire1:
            radiant1 = radiant1 + list_mmr[n]
            dire1 = dire1 + list_mmr[n+1]
            team_order1[n] = "Team 1"
            team_order1[n+1] = "Team 2"
        else:
            dire1 = dire1 + list_mmr[n]
            radiant1 = radiant1 + list_mmr[n+1]
            team_order1[n] = "Team 2"
            team_order1[n+1] = "Team 1"
    team_order2 = ['', '', '', '', '', '', '', '', '', '']
    radiant2 = 0
    dire2 = 0
    for n in range(8, -2, -2):
        if radiant2 == dire2 or radiant2 < dire2:
            radiant2 = radiant2 + list_mmr[n]
            dire2 = dire2 + list_mmr[n+1]
            team_order2[n] = "Team 1"
            team_order2[n+1] = "Team 2"
        else:
            dire2 = dire2 + list_mmr[n]
            radiant2 = radiant2 + list_mmr[n+1]
            team_order2[n] = "Team 2"
            team_order2[n+1] = "Team 1"
    average1 = (radiant1 / 5) - (dire1 / 5)
    average2 = (radiant2 / 5) - (dire2 / 5)
    print("Draft method")
    print(average1)
    print(average2)
    if abs(average1) < 100 and abs(average2) < 100:
        coin_flip = random.randint(1, 2)
        if coin_flip == 1:
            return team_order1
        else:
            return team_order2
    elif abs(average1) < abs(average2):
        return team_order1
    else:
        return team_order2

def sort_balancer(list_mmr):
    team_order1 = ["Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2"]
    radiant1 = list_mmr[0] + list_mmr[2] + list_mmr[4] + list_mmr[6] + list_mmr[8]
    dire1 = list_mmr[1] + list_mmr[3] + list_mmr[5] + list_mmr[7] + list_mmr[9]
    for n in range(8, 0, -2):
        if ((list_mmr[n] - list_mmr[n+1]) / 2) < ((radiant1 / 5) - (dire1 / 5)):
            team_order1[n] = "Team 2"
            team_order1[n+1] = "Team 1"
            radiant1 = radiant1 - list_mmr[n] + list_mmr[n+1]
            dire1 = dire1 + list_mmr[n] - list_mmr[n+1]
    team_order2 = ["Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2"]
    radiant2 = list_mmr[0] + list_mmr[2] + list_mmr[4] + list_mmr[6] + list_mmr[8]
    dire2 = list_mmr[1] + list_mmr[3] + list_mmr[5] + list_mmr[7] + list_mmr[9]
    for n in range(0, 10, 2):
        if ((list_mmr[n] - list_mmr[n + 1]) / 2) < ((radiant2 / 5) - (dire2 / 5)):
            team_order2[n] = "Team 2"
            team_order2[n + 1] = "Team 1"
            radiant2 = radiant2 - list_mmr[n] + list_mmr[n + 1]
            dire2 = dire2 + list_mmr[n] - list_mmr[n + 1]
    average1 = (radiant1 / 5) - (dire1 / 5)
    average2 = (radiant2 / 5) - (dire2 / 5)
    print("Sort method")
    print(average1)
    print(average2)
    if abs(average1) < 100 and abs(average2) < 100:
        coin_flip = random.randint(1, 2)
        if coin_flip == 1:
            return team_order1
        else:
            return team_order2
    elif abs(average1) < abs(average2):
        return team_order1
    else:
        return team_order2

def mean_balancer(list_mmr):
    team_order = ['', '', '', '', '', '', '', '', '', '']
    radiant = 0
    dire = 0
    radiant = radiant + list_mmr[4]
    team_order[4] = "Team 1"
    dire = dire + list_mmr[5]
    team_order[5] = "Team 2"
    if radiant < dire:
        radiant = radiant + list_mmr[2]
        team_order[2] = "Team 1"
        dire = dire + list_mmr[3]
        team_order[3] = "Team 2"
    else:
        radiant = radiant + list_mmr[3]
        team_order[3] = "Team 1"
        dire = dire + list_mmr[2]
        team_order[2] = "Team 2"
    if (radiant / 2) < (dire / 2):
        radiant = radiant + list_mmr[6]
        team_order[6] = "Team 1"
        dire = dire + list_mmr[7]
        team_order[7] = "Team 2"
    else:
        radiant = radiant + list_mmr[7]
        team_order[7] = "Team 1"
        dire = dire + list_mmr[6]
        team_order[6] = "Team 2"
    if (radiant / 3) < (dire / 3):
        radiant = radiant + list_mmr[0]
        team_order[0] = "Team 1"
        dire = dire + list_mmr[1]
        team_order[1] = "Team 2"
    else:
        radiant = radiant + list_mmr[1]
        team_order[1] = "Team 1"
        dire = dire + list_mmr[0]
        team_order[0] = "Team 2"
    if (radiant / 4) < (dire / 4):
        team_order[8] = "Team 1"
        team_order[9] = "Team 2"
    else:
        team_order[9] = "Team 1"
        team_order[8] = "Team 2"
    return team_order
