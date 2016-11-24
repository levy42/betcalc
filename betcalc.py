import storage
import time


def calculate(model_id, input_params):
    start = time.time()
    m = storage.get_model(model_id)
    h_params = {}
    for i, v in input_params.items():
        h_params[i] = (m['params'][i]['map'][v], m['params'][i]['range'])
    outcomes = []
    for i in m['stage1']:
        t = m['stage1'][i]
        if len(t['params']) == 1:
            hash_i = h_params[t['params'][0]][0]
        else:
            hash_i = _hash(h_params[t['params'][0]][0],
                           h_params[t['params'][1]][0],
                           h_params[t['params'][0]][1],
                           h_params[t['params'][1]][1])
        o_type = t['outcome_type']
        v = t['values'][hash_i]
        outcomes.append({'value': v, 'parameter': o_type['parameter'],
                         'name': o_type['name'],
                         'outcome_type_id': o_type['id']})
        if t['out_param']:
            h_params[t['out_param']['id']] = t['out_param']['map'][str(v)]
    for i in m.get('stage2', []):
        t = m['stage2'][i]
        if len(t['params']) == 1:
            hash_i = h_params[t['params'][0]][0]
        else:
            hash_i = _hash(h_params[t['params'][0]][0],
                           h_params[t['params'][1]][0],
                           h_params[t['params'][0]][0],
                           h_params[t['params'][1]][0])
        o_type = t['outcome_type']
        v = t['values'][hash_i]
        outcomes.append({'value': v, 'parameter': o_type['parameter'],
                         'name': o_type['name'],
                         'outcome_type_id': o_type['id']})
    print("Time: %s" % (time.time() - start))
    return outcomes


def _hash(p1, p2, range1, range2):
    return p1 * range2 + p2 if range1 > range2 else p2 * range1 + p1
