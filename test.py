import numpy as np
from keras.models import load_model


model = load_model('test.model')


mean = [3.68264337e+02, 2.25967367e-01, 8.64548766e-02, 1.15329634e+01]
std = [565.7039326, 116.71451414, 104.41504112, 1.67337289]

bpm = 180
rhythm = 1/2
tdelta = [60 * 1000 / bpm * rhythm for _ in range(3)]

def evaluate(xdelta, ydelta):
    data = np.array([tdelta, xdelta, ydelta], dtype=np.float).T
    data = (data - mean[:3]) / std[:3]

    data = data.reshape(1, *data.shape)
    prediction = model.predict(data)
    print('difficulty score:', prediction)
