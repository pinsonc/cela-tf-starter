import tensorflow as tf
from tensorflow import keras
import numpy as np
import boto3
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.optimizers import SGD

train_path = '/data/Resize/Training/' # directory containing subsets of data with labels
valid_path = '/data/Resize/Validation/'
test_path = '/data/Resize/Test/'

test_num = 164542 # number of original test images
ep = 10

train_datagen = keras.preprocessing.image.ImageDataGenerator()
valid_datagen = keras.preprocessing.image.ImageDataGenerator()
test_datagen = keras.preprocessing.image.ImageDataGenerator()

IMG_SHAPE = (224, 224, 3)

# Use the ImageDataGenerators to load the training data
train_gen = train_datagen.flow_from_directory(directory=train_path,
                                    target_size=(224,224), # size to resize images to
                                    color_mode='rgb', # color mode of the images
                                    batch_size=64, # how many images to process at once
                                    class_mode='categorical', # classify into categorical classes
                                    shuffle=True # shuffle order of images
)
valid_gen = valid_datagen.flow_from_directory(directory=valid_path,
                                    target_size=(224,224),
                                    color_mode='rgb',
                                    batch_size=64,
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

base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
                                               include_top=False, # don't include class layer at top, better for feature extraction
                                               weights='imagenet')

base_model.trainable = True

fine_tune_at = 100
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable =  False

model = keras.models.Sequential()
model.add(keras.layers.GlobalAveragePooling2D())
model.add(keras.layers.Dense(1, activation='sigmoid'))

model.compile(loss='categorical_crossentropy',
                optimizer=tf.keras.optimizers.RMSprop(lr=2e-5),
                metrics=['accuracy'])

model.summary()

model.fit_generator(train_datagen,
                    steps_per_epoch=STEP_SIZE_TRAIN,
                    epochs=ep,
                    workers=4,
                    validation_data=valid_datagen,
                    validation_steps=STEP_SIZE_VALID)

# evaluate the function using the test set
test_loss, test_acc = model.evaluate_generator(test_gen,
                                            test_num)

# print test accuracy
print('Accuracy: {}'.format(test_acc))