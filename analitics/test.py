import json
import math


# print(create_l(open("test.json").read()))
def get_outcomes():
    team1 = 'CSKA Moscow'
    team2 = 'Bayer 04 Leverkusen'
    outcomes = {}
    all = json.loads(open("test.json").read())
    for result in all['result_types']:
        for market_group in result['market_groups']:
            market_name = market_group['market_name']
            for market in market_group['markets']:
                for outcome in market['outcomes']:
                    name = market_name + ' ' + outcome['outcome_name']
                    if result['result_type_name'] != "Full Time":
                        name = result['result_type_name'] + ' ' + name
                    name = name.replace(team1, 'Home')
                    name = name.replace(team1, 'Home')
                    name = name.replace(team2, 'Away')
                    name = name.replace(team2, 'Away')
                    parts = name.split("(")
                    if len(parts) == 2 and parts[1] != "YES)":
                        type = "p"
                    else:
                        type = "c"
                    name = name.split("(")[0]
                    name.rstrip()
                    code = name.replace("Full Time", "FT")
                    code = code.replace("1st Half", "1H")
                    code = code.replace("2st Half", "2H")
                    code = code.replace("Odd / Even", "OE")
                    code = code.replace("Over/Under", "OU")
                    code = code.replace("Handicup", "HAND")
                    code = code.replace("Correct Score", "CS")
                    code = code.replace(" ", "_")
                    code = code.replace(":", "_")
                    code = code.replace("-", "_")
                    code = code.upper()
                    if code[-1] == "_":
                        code = code[:-1]
                    favbet_id = "%s_%s_%s" % (result['result_type_id'],
                                              market_group[
                                                  'market_template_id'],
                                              outcome['outcome_type_id'])
                    outcomes[name] = ({'name': name,
                                       'code': code,
                                       'sport_id': 1,
                                       'favbet_id': favbet_id,
                                       'type': type})
    open("outcomes.json", 'w').write(
            json.dumps(sorted(outcomes.values(), key=lambda k: k['code'])))
    print "finish"
    return outcomes


def get_outcome_values(all):
    outcomes = []
    for result in all['result_types']:
        for market_group in result['market_groups']:
            for market in market_group['markets']:
                x = 0
                for outcome in market['outcomes']:
                    x += 1 / float(outcome['outcome_coef'])
                for outcome in market['outcomes']:
                    parts = outcome['outcome_name'].split("(")
                    if len(parts) > 1 and parts[1] != "YES)":
                        parameter = parts[1][:-1]
                    else:
                        parameter = None
                    outcomes.append(
                            {'result_id': result['result_type_id'],
                             'id': outcome['outcome_type_id'], 'p': parameter,
                             'value': x / float(outcome['outcome_coef'])})
    return outcomes


AH_ID = 1
TOTAL_ID = 10
AH = ['-4.0', '-3.0', '-2.0', '-1.0', '0.0', '+3.0', '+2.0', '+1.0', '+4.0']
TOTAL = ['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0']


def get_params(outcomes):
    hands = []
    totals = []
    for o in outcomes:
        if o['id'] == AH_ID and o['p'] in AH and o['result'] == 'Full Time':
            hands.append(o)
        if o['id'] == TOTAL_ID \
                and o['p'] in TOTAL and o['result'] == 'Full Time':
            totals.append(o)
    hands = sorted(hands, key=lambda x: math.fabs(0.5 - x['value']))
    totals = sorted(totals, key=lambda x: math.fabs(0.5 - x['value']))
    hand1, hand2 = hands[0], hands[1]
    total1, total2 = totals[0], totals[2]
    expAH = hand1['value'] * int(float(hand1['p'])) + hand2['value'] * int(
            float(hand2['p']))
    expT = total1['value'] * int(float(total1['p'])) + total2['value'] * int(
            float(total2['p']))
    expHome = (expT - expAH) / 2
    expAway = expT - expHome
    return expHome, expAway


# outcomes = get_outcome_values(json.load(open("test.json")))
# print(get_params(outcomes))
get_outcomes()
