import json
import os.path
import requests
import time
import logging

LOG = logging.getLogger('Parser')
hdlr = logging.FileHandler('parser.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
LOG.addHandler(hdlr)
LOG.setLevel(logging.INFO)

DATA_DIR = 'data/'
INTERVAL = 60  # minutes

sport_ids = [1]
outcome_types = {o['favbet_id']: o for o in
                 json.loads(file("outcomes.json").read())}


def parse():
    LOG.info("Start parsing!")
    start = time.time()
    r = requests.get("https://www.favbet.com/bets/menu/?0.5676334469294224")
    leagues = []
    struct = json.loads(r.content)
    for s in struct['sports']:
        if s['sport_id'] not in sport_ids:
            continue
        for c in s['categories']:
            for t in c['tournaments']:
                leagues.append(t)
    succeded = 0
    failed = 0
    for l in leagues:
        d = {'tournaments': '{"tournaments":[%s]}' % l['tournament_id']}
        r = requests.post("https://www.favbet.com/bets/events/", d)
        data = json.loads(r.content)
        events = []
        for s in data['markets']:
            for t in s['tournaments']:
                for e in t['events']:
                    events.append(e)
        for event in events:
            try:
                parce_event(event)
                succeded += 1
            except Exception as e:
                failed += 1
                LOG.error("Failed to parce Event id %s. Reason: %s" % (
                    event['event_id'], e))
    delta = time.time() - start
    LOG.info("Finish! Succeded: %s, Falied: %s. Time: %s" % (
        succeded, failed, delta))


def parce_event(e):
    LOG.info("event. Id : %s" % e['event_id'])
    r = requests.get(
        "https://www.favbet.com/bets/events/%s?0.6296180333445982" %
        e['event_id'])
    all = json.loads(r.content)
    outcomes = {}
    head_market = all['head_market']
    m = 0
    if not head_market.get('outcomes'):
        LOG.info("event skipped, no outcomes!")
        return
    for outcome in head_market['outcomes']:
        m += 1.0 / float(outcome['outcome_coef'])
    m = 1 / m
    outcomes['1'] = {
        'value': round(m / head_market['outcomes'][0]['outcome_coef'],
                       3),
        'code': '1', 'parameter': None}
    outcomes['X'] = {
        'value': round(m / head_market['outcomes'][1]['outcome_coef'],
                       3),
        'code': 'X', 'parameter': None}
    outcomes['2'] = {
        'value': round(m / head_market['outcomes'][2]['outcome_coef'],
                       3),
        'code': '2', 'parameter': None}
    e_hash = int(outcomes['1']['value'] * 1000000 + outcomes['X'][
        'value'] * 1000)
    for result in all['result_types']:
        for market_group in result['market_groups']:
            for market in market_group['markets']:
                m = 0.0
                for outcome in market['outcomes']:
                    m += 1.0 / float(outcome['outcome_coef'])
                if m > 2:
                    m -= 1
                m = 1 / m
                for outcome in market['outcomes']:
                    favbet_id = "%s_%s_%s" % (result['result_type_id'],
                                              market_group[
                                                  'market_template_id'],
                                              outcome[
                                                  'outcome_type_id'])
                    o = outcome_types.get(favbet_id)
                    if not o:
                        continue
                    code = o['code']
                    parts = outcome['outcome_name'].split("(")
                    parameter = None
                    if len(parts) > 1:
                        try:
                            parameter = float(parts[1][:-1])
                            code = "%s_%s" % (code, parameter)
                        except Exception as e:
                            pass
                    value = round(m / outcome[
                        'outcome_coef'], 3)
                    outcomes[code] = {'code': code,
                                      'parameter': parameter,
                                      'value': value,
                                      'coef': outcome['outcome_coef']}
    path = "%s%s_%s.json" % (DATA_DIR, all['sport_id'], e_hash)
    if not os.path.isfile(path):
        file(path, 'w').write(json.dumps(outcomes))
    else:
        existing = json.loads(file(path).read())
        sum = dict(existing.items() + outcomes.items())
        file(path, 'w').write(json.dumps(sum))


if __name__ == '__main__':
    i = INTERVAL
    while True:
        if i == INTERVAL:
            try:
                parse()
            except Exception as e:
                LOG.error(e)
            i = 0
        LOG.info("%s min left to next parsing" % (INTERVAL - i))
        time.sleep(60)
        i += 1
