# Test TensorFlow Model for Image Processing on Locally Stored Data
This is meant to be a simple test of a custom data extraction, labeling, and machine learning script that I wrote for a research lab.

Currently it is scaled in such a way that gives no meaningful results for the dataset we are using within the lab. But with the proper file structure and data could yield meaningful results on other sets of data still.

## `splitdata.py`
This script takes the `.csv` output from a `.xslx` file and outputs the procedure, start frame and end frame to its own file in folder `/framecsv`

It also gives each procedure its own `.csv` file in the `/Data/ALL` with start and end times. Then it puts those in a distribution (given by `count.py`) in the training, validation, and test subsets.

## `label.py`
Takes the procedure files from `spiltdata.py` and the frames from an extracted video and puts them in the corresponding procedure folder (label) in the corresponding subset's folder

## `tfimage.py`
Loads the image data into TensorFlow and runs a simple neural network.

## TODO
* I need to input the full dataset (multiple camera angles across many subjects)
* I need to run this script remotely on a cloud GPU (EC2 or Google Colab) so it's run in a reasonable time (takes a full workday on my machine with only one video)
* Make this GitHub repo actually useful for other people lol
