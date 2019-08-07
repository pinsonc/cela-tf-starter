# Test TensorFlow Model for Image Processing on Locally Stored Data
Custom data extraction, labeling, and machine learning script that I wrote for the Learning in Virtual Environments (LIVE) research lab at Vanderbilt University

## Running on EC2

First, on the GitHub, there is a folder called “rawcsv” that has 7 .csv files in it. Each of these files contain the procedures for one subject as well as the start and end time of the video. The folder `/framecsv` is much the same except that the time is given in “start and stop frame of the video” rather than timestamps (framecsv files are the output from the first half of the `splitdata.py` file). The files in framecsv are used to create procedure-specific csvs for each subject. This also happens in `splitdata.py`. So, in short, you will end up with a folder for each test subject underneath the `/Data` folder that each contain one csv file for each procedure. Each of these csv files have a list of ranges where that procedure occurs. These are what we will be using to actually label the images later down the line.

Switching gears for a moment, we need to actually obtain the frames. To do this, we will use a CLI tool called [ffmpeg](https://ffmpeg.org/). The video data is split into 8 minute chunks. So we first need to concatenate the videos together. This way, the frames will be continuously numbered. It saves us some work in the end. Then, after concatenation, we need to split each video into its constituent frames. I recommend installing the GPU-enabled version and running it on an EC2 instance if possible because it is rather intensive and I ran into a number of issues running it locally. Just make sure you attach an EBS drive because it will be a lot of data. Here are the commands I used (again, Ubuntu-specific. Google around for similar Windows ones if needed):

```
# generates a list of all MP4s, run in folder of a single subject
printf "file '%s'\n" ./*.MP4 > mylist.txt
# concatenate all videos in mylist.txt
ffmpeg -f concat -safe 0 -i mylist.txt -c copy output
```
```
# create a frames directory
mkdir frames
# extract all frames
ffmpeg -i output.MP4 -s 224x224 frames/thumb%06d.jpg -hide_banner
```
```
# upload files to s3, only add debug if you want to see verbose output
aws s3 sync frames s3://bucket-name/path/to/object --debug
```
*Note: I did not use the -s flag and the resolution when I extracted my files. However, I did end up resizing them later and it is necessary to resize them eventually. So I recommend doing this now if possible. It’ll save you a step.*

After each video is uploaded to their own subject folder in AWS (I had a Raw Data object with folders S1C2, S2C2, … under it to hold all the raw frames for each subject). You can use the script `awslabel.py` to organize the data into their correct subdirectories and labels. In my testing, I had subjects 1 through 5 in Training, 6 in Validation, and 7 in Test. And that what `awslabel.py` is currently set to do.

Now all the frames are on an S3 bucket. Next you need to create and set up an EC2 instance. First, make sure you are in the same region as your S3 bucket (cela-input is on N. Virginia or us-east-1). You can change your region for EC2 and other services at the top right of the console (console = AWS website). Create a new instance. To pick an AMI and Instance Type I would do some research around Amazon’s website but, as an example, I chose the Ubuntu-based Deep Learning Base AMI for obvious reasons and the p3.2xlarge instance type for its GPU performance. Finally, on creation, you will want to attach an EBS storage volume that is large enough to hold all of the data you have on your S3 bucket that you want to do operations on. The type really depends on the data size and cost limitations but I chose the SSD.

*Ensure when you create your EC2 instance that you download the .pem file and keep it somewhere safe. It is your only way of logging into your virtual machine!*

To SSH into the virtual machine, you can use the terminal on Ubuntu/Mac or PuTTY SSH Client on Windows. Personally, I used the Ubuntu terminal because PuTTY wasn’t allowing me to copy and paste commands to the EC2 instance. Here is the SSH command I used for that on Ubuntu:

```
ssh -i private_key.pem AMI_username@Public_DNS
```

The AMI_username can be found depending on which AMI you chose for your instance. For Ubuntu-based distributions, it is ubuntu. For Amazon Linux, it is ec2-user. The others you can quickly Google. The Public DNS is available on the EC2 console.

Once in the instance, you have to manually mount your EBS drive. Find the name of the drive using the lsblk command. Then do the following series of commands:

```
sudo su # switch to root
lsblk # get the drive path
sudo file -s /drive/path # check if there is a file system on the drive
# --ONLY-- IF THE ABOVE OUTPUT IS /drive/path: data
sudo mkfs -t ext4 /drive/path # REFORMATS DRIVE,
cd / # navigate to the root director
mkdir data # make a place for the data to live
mount /drive/path /data # mount the drive to the file system
cd /data # navigate to your newly mounted drive
```
Now your drive is present at the /data directory and you can use it like any other directory.

Setting up anything needed on the instance can be done just like you would on a normal Ubuntu machine. One note is that when using pip to install TensorFlow, make sure you install the GPU-enabled version if you are using an instance with a GPU.

Now that you are in your EC2 instance and you’ve mounted your EBS drive, you can use the following command to sync your data.

```
aws s3 cp s3://bucket-name/path/to/data Data --recursive
```
**The --recursive flag is necessary or the script will only get files at parent-level.**

After getting your data synced, I would recommend getting any scripts to the instance by first uploading them to S3 and copying them (cp) the same way you just did that (no --recursive though). So now you have an EC2 instance with your three data sets, and your Python Scripts ready to go. The scripts are written in Python 3 which should come pre-installed on the Ubuntu Deep Learning AMI. Make sure you use pip3 to install any needed packages. I followed the errors to see what I needed to install or what small tweaks I needed to make to the scripts using Vim (namely, don’t forget to change the file path for the data)

And there you go! That should get you up and running on the ML code I wrote. It should also hopefully explain the main pipeline I used for this. `resizer.py` is there in case you couldn’t resize the frames as you extracted them. And `label.py` is worthless. Just a local version of `awslabel.py`.

## The Scripts

### `awslabel.py`
Given that the frames are in folders by subject in an S3 bucket, this can take the images from each folder and relocate them to the file structure Data/Training/Label/File on the S3 bucket. I did this so I could batch upload the frames by subject and camera angle and then worry about labeling them later. It is worth noting that when I extracted the frames, I used the naming convention [subject number][camera number][frame number].jpg so that I could easily parse all this data from the file name for labeling purposes.

### `clean.py`
The single function in this file deletes all files in a given directory. I used it when I was testing locally to save space each time I tried running label scripts.

### `count.py`
This is another file for local testing that takes a single subject and splits each of its procedures into test, validation, and training data.

### `ec2.py`
This script just automates the SSH process. So you can log in, run tasks, and get the outputs into Python. It has some potential to make scripts but I never played with it much. It was just when I thought I would need to interface more directly with EC2 from within Python.

### `label.py`
Takes the procedure files from `spiltdata.py` and the frames from an extracted video and puts them in the corresponding procedure folder (label) in the corresponding subset's folder

### `resizer.py`
This script downloads a file from S3, converts it to dimensions 224x224, uploads the new version as a copy to S3, and then deletes it off the hard drive. I did this so that I could save the EC2 instance the time and processing power (and money) to convert them while the code is running.

### `splitdata.py`
This script takes the csv output from a .xslx file and outputs the procedure, start frame and end frame to its own file in folder framecsv. All procedures are also given their own csv with start and end frames in Data/ALL. To make them all uniform, I created a second row that has all of the names of the procedures where they are capitalized throughout. That means that the label is actually row 1 and not row 0. This basically creates the files I used to label all the frames in the other scripts.

### `tfimage.py`
Loads the image data into TensorFlow and runs a simple neural network.

### `tfimagetemp.py`
This is an attempt to set up an LSTM in the same tfimage.py code from above.

## Additional Documentation
[This Google Doc](https://docs.google.com/document/d/1meS-vAqsS7E8b26omvotoGY7mfBzj1pn7bqyfyGafkk/edit?usp=sharing) Has way more information about this GitHub as well as my summer activities and some great general information on deep learning.
