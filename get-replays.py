import json
import time
import sys
import os

import requests
from tqdm import tqdm

import api


REQUESTS_PER_MINUTE = 10

with open('beatmap-scores.json') as fd:
    scores = json.loads(fd.read())

url = "https://osu.ppy.sh/api/get_replay"
for beatmap in tqdm(sorted(scores.keys())):
    beatmap_path = os.path.join('data', beatmap)
    if not os.path.exists(beatmap_path):
        os.makedirs(beatmap_path)
    for user in tqdm(sorted(scores[beatmap])):
        start_time = time.perf_counter()
        path = os.path.join(beatmap_path, '{}.b64'.format(user))
        if os.path.exists(path):
            continue
        payload = {
            'k': api.key,
            'u': user,
            'b': beatmap,
        }
        success = False
        while not success:
            try:
                r = requests.get(url, params=payload)
                r.raise_for_status()
                results = json.loads(r.text)
                success = True
            except Exception as e:
                print('ERROR ({}): {}'.format(user_id, e), file=sys.stderr)
                time.sleep(60/REQUESTS_PER_MINUTE)

        with open(path, 'w') as fd:
            fd.write(results['content'])
        end_time = time.perf_counter()
        time_diff = end_time - start_time
        wait_time = max(0, 60/REQUESTS_PER_MINUTE - time_diff)
        time.sleep(wait_time)
