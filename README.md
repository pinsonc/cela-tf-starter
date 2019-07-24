# Test TensorFlow Model for Image Processing on Locally Stored Data
This is meant to be a simple test of a custom data extraction, labeling, and machine learning script that I wrote for the Learning in Virtual Environments (LIVE) research lab at Vanderbilt University

## `awslabel.py`
Moves the AWS keys stored in an S3 Bucket to the correct file structure.

## `clean.py` & `count.py`
Supporting functions for my local testing

## `ec2.py`
Connects to and runs commands on an EC2 instance

## `label.py`
Takes the procedure files from `spiltdata.py` and the frames from an extracted video and puts them in the corresponding procedure folder (label) in the corresponding subset's folder

## `splitdata.py`
This script takes the `.csv` output from a `.xslx` file and outputs the procedure, start frame and end frame to its own file in folder `/framecsv`

It also gives each procedure its own `.csv` file in the `/Data/ALL` with start and end times. Then it puts those in a distribution (given by `count.py`) in the training, validation, and test subsets.

## `subj.py`
Generates csv data for all subjects (adapted version of `splitdata.py`, which only did one subject)

## `tfimage.py`
Loads the image data into TensorFlow and runs a simple neural network.
