import math
import json
from os import listdir
from os.path import isfile, join


def get_params(outcomes):
    hands = []
    totals = []
    for o in outcomes:
        if not o['parameter'] or not o['parameter'].is_integer():
            continue
        else:
            code = o['code'].rsplit("_", 1)[0]
        if code == 'HANDICAP_HOME':
            hands.append(o)
        if code == 'OU_OVER':
            totals.append(o)
    hands = sorted(hands, key=lambda x: math.fabs(0.5 - x['value']))
    totals = sorted(totals, key=lambda x: math.fabs(0.5 - x['value']))
    if len(hands) < 2:
        return None
    if len(totals) < 2:
        return None
    hand1, hand2 = hands[0], hands[1]
    total1, total2 = totals[0], totals[1]
    expAH = hand1['value'] * int(float(hand1['parameter'])) + hand2[
                                                                  'value'] * int(
            float(hand2['parameter'])) / (hand1['value'] + hand2['value'])
    expT = total1['value'] * int(float(total1['parameter'])) + total2[
                                                                   'value'] * int(
            float(total2['parameter'])) / (total1['value'] + total2['value'])
    expHome = (expT - expAH) / 2
    expAway = expT - expHome
    if expHome < 0 or expAway < 0:
        print("Error: value < 0, values: %s"
              % [hand1['parameter'], hand1['value'],
                 hand2['parameter'], hand2['value'],
                 total1['parameter'], total1['value'],
                 total2['parameter'],
                 total2['value']])
        return None
    return round(expHome, 1), round(expAway, 1)


def analize():
    files = [f for f in listdir("data/") if isfile(join("data/", f))]
    param_map = {}
    values_map = {}
    for path in files:
        outcomes = json.loads(file("data/" + path).read())
        params = get_params(outcomes.values())
        if not params:
            print("Skip")
            continue
        param_map[path.split(".")[0]] = params
        param_str = '%s_%s' % (params[0], params[1])
        if not values_map.get(param_str):
            values_map[param_str] = []
            values_map[param_str].append(path)
        values_map[param_str].append(path)
        print(".")
    print("Saving results...")
    file("map_path", "w").write(json.dumps(param_map))
    file("map_param", "w").write(json.dumps(values_map))
    print("Finish!")


analize()
