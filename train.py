import itertools

import numpy as np
import h5py
from keras.models import Model
from keras.layers import Activation, Dense, Input
from keras.layers.recurrent import LSTM


HITOBJECT_LENGTH = 2


file = h5py.File('data.hdf5')
data = [file[k][()] for k in file]


def nwise(iterable, n):
    ''' s -> (s0, s1, ... sn), (s1, s2, ... sn+1), ... '''
    iters = itertools.tee(iterable, n)
    for i, it in enumerate(iters):
        for _ in range(i):
            next(it, None)
    return zip(*iters)


def data_gen(data_src):
    for beatmap in data_src:
        for chunk in nwise(beatmap, HITOBJECT_LENGTH):
            x = [entry[:3] for entry in chunk]
            y = chunk[-1][3]
            yield x, y


all_objects = np.vstack(data)
mean = np.mean(all_objects, axis=0)
mean[1:3] = np.mean(mean[1:3])
std = np.std(all_objects, axis=0)
std[1:3] = np.mean(std[1:3])
print('mean', mean)
print('std', std)

data = [(beatmap - mean) / std for beatmap in data]
X = []
Y = []
for x, y in data_gen(data):
    X.append(x)
    Y.append(y)
X = np.array(X)
Y = np.array(Y)
rng = np.random.get_state()
np.random.shuffle(X)
np.random.set_state(rng)
np.random.shuffle(Y)


input = Input(shape=(HITOBJECT_LENGTH, 3))
x = input
x = LSTM(32)(x)
x = Dense(256)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(1)(x)

model = Model(input=input, output=x)
model.compile(loss='mse', optimizer='adam')

model.fit(X, Y, validation_split=0.2, batch_size=4096, nb_epoch=50)
model.save('test.model')
