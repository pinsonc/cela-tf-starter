import tensorflow as tf
import numpy as np
import boto3
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.optimizers import SGD

train_path = '/data/Data/Training/'
valid_path = '/data/Data/Validation/'
test_path = '/data/Data/Test/'

# image resolution and color channels
img_w = 3840
img_h = 2160
img_chan = 3

nb_classes = 10
test_num = 317 #number of test images

train_datagen = keras.preprocessing.image.ImageDataGenerator()
valid_datagen = keras.preprocessing.image.ImageDataGenerator()
test_datagen = keras.preprocessing.image.ImageDataGenerator()

# Use the ImageDataGenerators to load the training data
train_gen = train_datagen.flow_from_directory(directory=train_path,
                                    target_size=(224,224),
                                    color_mode='rgb',
                                    batch_size=32,
                                    class_mode='categorical',
                                    shuffle=True
)
valid_gen = valid_datagen.flow_from_directory(directory=valid_path,
                                    target_size=(224,224),
                                    color_mode='rgb',
                                    batch_size=32,
                                    class_mode='categorical',
                                    shuffle=True
)
test_gen = test_datagen.flow_from_directory(directory=test_path,
                                    target_size=(224,224),
                                    color_mode='rgb',
                                    batch_size=1,
                                    class_mode='categorical',
                                    shuffle=False
)

# Calculate the different step sizes based on the number of photos in the
# generator and the batch size
STEP_SIZE_TRAIN=train_gen.n//train_gen.batch_size
STEP_SIZE_VALID=valid_gen.n//valid_gen.batch_size

# set up model
model = keras.models.Sequential()
model.add(keras.layers.Conv2D(32, (3, 3), input_shape=(224, 224, 3)))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

model.add(keras.layers.Conv2D(32, (3, 3)))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

model.add(keras.layers.Conv2D(64, (3, 3)))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

model.add(keras.layers.Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(keras.layers.Dense(64))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.Dropout(0.5))
model.add(keras.layers.Dense(1))

model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(64, activation='relu'))
model.add(keras.layers.Dense(28, activation='softmax'))

model.summary() # print structure of the model

opt = keras.optimizers.SGD(lr=0.01) # custom SGD optimizer

# compile the model with a loss function, optimizer, and the metric on which to judge it
model.compile(loss='categorical_crossentropy',
            optimizer=opt,
            metrics=['accuracy']
)

# train the neural net
with tf.device('/GPU:0'):
    model.fit_generator(generator=train_gen,
                        steps_per_epoch=STEP_SIZE_TRAIN,
                        validation_data=valid_gen,
                        validation_steps=STEP_SIZE_VALID,
                        epochs=1
    )

#  the function using the test set
test_loss, test_acc = model.evaluate_generator(test_gen,
                                            test_num)

# print test accuracy
print('Accuracy: {}'.format(test_acc))
