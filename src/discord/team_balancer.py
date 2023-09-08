def draft_balancer(list_mmr):
    team_order = []
    radiant = 0
    dire = 0
    radiant = radiant + list_mmr[0] + list_mmr[-1]
    team_order.append("Team 1")
    dire = dire + list_mmr[1] + list_mmr[-2]
    team_order.append("Team 2")
    if radiant > dire:
        dire = dire + list_mmr[2]
        radiant = radiant + list_mmr[3]
        team_order.append("Team 2")
        team_order.append("Team 1")
    else:
        radiant = radiant + list_mmr[2]
        dire = dire + list_mmr[3]
        team_order.append("Team 1")
        team_order.append("Team 2")
    if radiant > dire:
        dire = dire + list_mmr[4]
        radiant = radiant + list_mmr[5]
        team_order.append("Team 2")
        team_order.append("Team 1")
    else:
        radiant = radiant + list_mmr[4]
        dire = dire + list_mmr[5]
        team_order.append("Team 1")
        team_order.append("Team 2")
    if radiant > dire:
        team_order.append("Team 2")
        team_order.append("Team 1")
    else:
        team_order.append("Team 1")
        team_order.append("Team 2")
    team_order.append("Team 2")
    team_order.append("Team 1")
    return team_order


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
