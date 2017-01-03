import json
import sys
import os

import requests
from tqdm import tqdm


with open('beatmaps.csv') as fd:
    beatmaps = fd.read().split(',')

session = requests.Session()
url = "https://osu.ppy.sh/osu/{}"
for beatmap in tqdm(beatmaps):
    success = False
    while not success:
        try:
            path = os.path.join('data', beatmap, '{}.osu'.format(beatmap))
            if os.path.isfile(path):
                with open(path) as fd:
                    if len(fd.read()) > 10:
                        success = True
                        continue
            r = session.get(url.format(beatmap))
            r.raise_for_status()
            result = r.text
            if len(result) < 10:
                raise ValueError('Result too short')
            with open(path, 'w') as fd:
                fd.write(result) 
            success = True
        except Exception as e:
            print('ERROR ({}): {}'.format(beatmap, e), file=sys.stderr)
