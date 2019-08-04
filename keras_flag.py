import numpy
import tensorflow
from tensorflow import keras
from tensorflow.keras.applications.mobilenet import MobileNet, \
        preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

import os, sys
# https://www.pyimagesearch.com/2019/06/24/change-input-shape-dimensions-for-fine-tuning-with-keras/

model = MobileNet(weights='imagenet')

img = image.load_img('data/P1090019.JPG', target_size=(224,224))
x = image.img_to_array(img)
x = numpy.expand_dims(x, axis=0)
x = preprocess_input(x)

preds = model.predict(x)

print('Predicted:', decode_predictions(preds, top=3)[0])

