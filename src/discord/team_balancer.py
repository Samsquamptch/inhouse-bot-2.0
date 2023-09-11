import random


def draft_balancer(list_mmr):
    team_order1 = ['', '', '', '', '', '', '', '', '', '']
    radiant1 = 0
    dire1 = 0
    for n in range(0, 10, 2):
        if radiant1 == dire1 or radiant1 < dire1:
            radiant1 += list_mmr[n]
            dire1 += list_mmr[n + 1]
            team_order1[n] = "Team 1"
            team_order1[n + 1] = "Team 2"
        else:
            dire1 = dire1 + list_mmr[n]
            radiant1 = radiant1 + list_mmr[n + 1]
            team_order1[n] = "Team 2"
            team_order1[n + 1] = "Team 1"
    team_order2 = ['', '', '', '', '', '', '', '', '', '']
    radiant2 = 0
    dire2 = 0
    for n in range(8, -2, -2):
        if radiant2 == dire2 or radiant2 < dire2:
            radiant2 += list_mmr[n]
            dire2 += list_mmr[n + 1]
            team_order2[n] = "Team 1"
            team_order2[n + 1] = "Team 2"
        else:
            dire2 = dire2 + list_mmr[n]
            radiant2 = radiant2 + list_mmr[n + 1]
            team_order2[n] = "Team 2"
            team_order2[n + 1] = "Team 1"
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
        if ((list_mmr[n] - list_mmr[n + 1]) / 2) < ((radiant1 / 5) - (dire1 / 5)):
            team_order1[n] = "Team 2"
            team_order1[n + 1] = "Team 1"
            radiant1 -= list_mmr[n]
            radiant1 += list_mmr[n + 1]
            dire1 += list_mmr[n]
            dire1 -= list_mmr[n + 1]
    team_order2 = ["Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2"]
    radiant2 = list_mmr[0] + list_mmr[2] + list_mmr[4] + list_mmr[6] + list_mmr[8]
    dire2 = list_mmr[1] + list_mmr[3] + list_mmr[5] + list_mmr[7] + list_mmr[9]
    for n in range(0, 10, 2):
        if ((list_mmr[n] - list_mmr[n + 1]) / 2) < ((radiant2 / 5) - (dire2 / 5)):
            team_order2[n] = "Team 2"
            team_order2[n + 1] = "Team 1"
            radiant2 -= list_mmr[n]
            radiant2 += list_mmr[n + 1]
            dire2 += list_mmr[n]
            dire2 -= list_mmr[n + 1]
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
    team_order1 = ['', '', '', '', '', '', '', '', '', '']
    radiant1 = 0
    dire1 = 0
    for n in range(0, 5, 1):
        if radiant1 == dire1 or radiant1 < dire1:
            radiant1 += list_mmr[4 - n]
            dire1 += list_mmr[5 + n]
            team_order1[4 - n] = "Team 1"
            team_order1[5 + n] = "Team 2"
        else:
            dire1 += list_mmr[4 - n]
            radiant1 += list_mmr[5 + n]
            team_order1[4 - n] = "Team 2"
            team_order1[5 + n] = "Team 1"
    team_order2 = ['', '', '', '', '', '', '', '', '', '']
    radiant2 = 0
    dire2 = 0
    for n in range(0, 5, 1):
        if radiant2 == dire2 or radiant2 < dire2:
            radiant2 += list_mmr[n]
            dire2 += list_mmr[-(n + 1)]
            team_order2[n] = "Team 1"
            team_order2[-(n + 1)] = "Team 2"
        else:
            dire2 += list_mmr[n]
            radiant2 += list_mmr[-(n + 1)]
            team_order2[n] = "Team 2"
            team_order2[-(n + 1)] = "Team 1"
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
