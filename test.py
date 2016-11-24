import json
import random
# sample = json.dumps([random.randint(1, 100) / 100. for x in range(10000)])
# model = json.loads(open("models/simple/simple.json").read())
# model['stage1'] = {}
#
# for i in range(1000):
#     model['stage1'][i] = {
#         "out_param": None,
#         "params": [
#             0,
#             1
#         ],
#         "outcome_type": {
#             "code": "FK%s" % i,
#             "parameter": 0.99,
#             "id": i,
#             "name": "Fake outcome %s" % i
#         }
#     }
#     open("models/test/outcomes/FK%s" % i, 'w').write(sample)
# open("models/test/test.json", 'w').write(json.dumps(model))
import time

start = time.time()
for i in range(300):
    f = open("tmp")
    f.seek(i)
    a = f.read(1)
print(time.time() - start)