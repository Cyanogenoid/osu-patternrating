import numpy as np


def parse_beatmap(s):
    beatmap = [float(x) for x in s.split(',') if x != '\n']
    beatmap = list(map(float, s.split(',')[:-1]))
    beatmap = np.array(beatmap).reshape(len(beatmap) // 3, 3)
    return beatmap


def parse_replay(s):
    replay = [float(x) if x else np.nan for x in s]
    replay = np.array(replay).reshape(len(replay) // 2, 2)
    return replay


with open('osuReplayAnalyzer/log.txt') as fd:
    beatmap = parse_beatmap(next(fd))
    replays = np.zeros([50, beatmap.shape[0], 2])
    for i, line in enumerate(fd):
        # TODO treat hr and dt mod combinations differently
        # for now, just pretend they're all nomod...
        hr, dt, *replay = line.split(',')
        replays[i, :, :] = parse_replay(replay)


times = beatmap[:, 0]
x = beatmap[:, 1]
y = beatmap[:, 2]
mean = np.nanmean(replays, axis=0)
delta = beatmap[:, 1:] - mean
stdev_2d = np.nanstd(replays, axis=0)
stdev = np.sqrt(np.sum(stdev_2d * stdev_2d, axis=1))

data = np.zeros([beatmap.shape[0], beatmap.shape[1] + 1])
data[:, :3] = beatmap
data[:, 3] = stdev
# TODO add mean difference if it seems useful
# TODO include correlation information
# TODO beatmap difficulty metadata