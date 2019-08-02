# Test TensorFlow Model for Image Processing on Locally Stored Data
This is meant to be a simple test of a custom data extraction, labeling, and machine learning script that I wrote for the Learning in Virtual Environments (LIVE) research lab at Vanderbilt University

[This Google Doc](https://docs.google.com/document/d/1meS-vAqsS7E8b26omvotoGY7mfBzj1pn7bqyfyGafkk/edit?usp=sharing) Has way more information about this GitHub as well as my summer activities and some great general information on deep learning.

## `awslabel.py`
Given that the frames are in folders by subject in an S3 bucket, this can take the images from each folder and relocate them to the file structure Data/Training/Label/File on the S3 bucket. I did this so I could batch upload the frames by subject and camera angle and then worry about labeling them later. It is worth noting that when I extracted the frames, I used the naming convention [subject number][camera number][frame number].jpg so that I could easily parse all this data from the file name for labeling purposes.

## `clean.py`
The single function in this file deletes all files in a given directory. I used it when I was testing locally to save space each time I tried running label scripts.

## `count.py`
This is another file for local testing that takes a single subject and splits each of its procedures into test, validation, and training data.

## `ec2.py`
This script just automates the SSH process. So you can log in, run tasks, and get the outputs into Python. It has some potential to make scripts but I never played with it much. It was just when I thought I would need to interface more directly with EC2 from within Python.

## `label.py`
Takes the procedure files from `spiltdata.py` and the frames from an extracted video and puts them in the corresponding procedure folder (label) in the corresponding subset's folder

## `resizer.py`
This script downloads a file from S3, converts it to dimensions 224x224, uploads the new version as a copy to S3, and then deletes it off the hard drive. I did this so that I could save the EC2 instance the time and processing power (and money) to convert them while the code is running.

## `splitdata.py`
This script takes the csv output from a .xslx file and outputs the procedure, start frame and end frame to its own file in folder framecsv. All procedures are also given their own csv with start and end frames in Data/ALL. To make them all uniform, I created a second row that has all of the names of the procedures where they are capitalized throughout. That means that the label is actually row 1 and not row 0. This basically creates the files I used to label all the frames in the other scripts.

## `tfimage.py`
Loads the image data into TensorFlow and runs a simple neural network.

## `tfimagetemp.py`
This is an attempt to set up an LSTM in the same tfimage.py code from above.
