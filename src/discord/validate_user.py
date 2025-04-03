def check_role_priority(user):
    core_roles = [user[0], user[1], user[2]]
    supp_roles = [user[3], user[4]]
    if 5 in core_roles and 5 not in supp_roles:
        role_pref = "Core"
    elif 5 in supp_roles and 5 not in core_roles:
        role_pref = "Support"
    else:
        core_avg = sum(core_roles) / 3
        supp_avg = sum(supp_roles) / 2
        role_balance = core_avg - supp_avg
        match role_balance:
            case _ if role_balance < 0:
                role_pref = "Support"
            case _ if role_balance > 1:
                role_pref = "Core"
            case _:
                role_pref = "Balanced"
    return role_pref
