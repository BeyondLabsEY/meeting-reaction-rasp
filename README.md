# Meeting Reaction 

It is a solution that consists of using an IoT device based on Raspberry Pi integrated with touch screen and connected to a microphone with bluetooth and camera using USB (_webcam_). This device, when triggered, will record a particular meeting or session, through actions on the device screen user interface.

During the meeting the audios and images will be processed continously in managed artificial intelligence services APIs such as _speech to text_ and _facial analysis_ to convert the audio into plain text. Subsequently these data will be analyzed to compose a graph of words most used during the sessions, in order to highlight the main discussions and, the images will track the attention and _Wow Moments_ while the session.

## Service Stack

The entire stack was based on the Python 3 programming language and the _Serverless_ model.

The generated audios are broken at 8-second intervals because of the _text to speech_ API restriction. After the file is separated, they are sent to an object cloud storage, the _Azure Blob Storage_. Then, a queue request is sent to no_Azure Storage Queues_.

When there is at least one item in the queue the execution of a function is automatically triggered by using _Azure Functions_ for data processing.

In the same way, the image analysis works.

The results are stored using the _Azure Storage Tables_ structure, a _nosql_ key-value table format.

- [x] Desktop Raspberry Pi Python 3 app (this)
- [x] OpenCV 3.4 in the desktop app (this)
- [x] Back-end Azure Functions 2 ([repo](https://github.com/BeyondLabsEY/meeting-reaction-functions))
- [x] Front-end React ([repo](https://github.com/BeyondLabsEY/meeting-reaction-web))


The infrastructured used is Azure.

- [x] Azure account
- [x] Region availability to use Azure Functions 2.0
- [x] Azure Blob storage
- [x] Azure Table
- [x] Azure Queue
- [x] Azure Face Recognition
- [x] Azure Text to Speech

## Components Installation

### Audio for microphone

It is necessary to install the package below for proper operation of the _PyAudio_.

```bash
sudo apt-get install portaudio19-dev
```

### OpenCV

Orinally from [Life2Coding](https://www.life2coding.com/install-opencv-3-4-0-python-3-raspberry-pi-3/).

Assuming you have Python 3 installed.

#### Expand filesystem

Type the following command to expand the Raspberry Pi3 file system

```bash
sudo raspi-config
```

Then select the following

```
Advanced Options > A1 Expand filesystem > Press “Enter”
```

It will show a message “The root partition has been resized”.

Then you need to reboot your pi using the following command.

```bash
sudo shutdown -r now
```

#### Freeing up some space

The default OS will take around 15% if you are using 32GB card. But if you are using a 8GB memory card it might take 50% of all your space. So, it is better to remove some unused packages like LibreOffice and Wolfram engine to free up some space on your pi.

You can do it simply typing the following command on the terminal window.

```bash
sudo apt-get purge wolfram-engine
sudo apt-get purge libreoffice*
sudo apt-get clean
sudo apt-get autoremove
```

#### Install dependencies

The first step is to update and upgrade any existing packages:

```bash
sudo apt-get update 
sudo apt-get upgrade
```

If you have been shown any error to fix you can type the following

```bash
sudo apt-get upgrade --fix-missing
```

Then reboot your pi.

```bash
sudo shutdown -r now
```

After your pi boots up start the Terminal again. Do the following.

Install CMAKE developer packages

```bash
sudo apt-get install build-essential cmake pkg-config -y
```

Install Image I/O packages

```bash
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev -y
```

Install Video I/O packages

```v
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt-get install libxvidcore-dev libx264-dev -y
```

Install the GTK development library for basic GUI windows

```bash
sudo apt-get install libgtk2.0-dev libgtk-3-dev -y
```

Install optimization packages (improved matrix operations for OpenCV)

```bash
sudo apt-get install libatlas-base-dev gfortran -y
```

#### Download the OpenCV 3.4 and contrib extra modules
```bash
cd ~
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.0.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.0.zip
unzip opencv_contrib.zip
```

#### Compile and install OpenCV 3.4.0 for Python 3
```bash
cd opencv-3.4.0
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D BUILD_opencv_java=OFF \
-D BUILD_opencv_python2=OFF \
-D BUILD_opencv_python3=ON \
-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D BUILD_EXAMPLES=ON\
-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.0/modules \
-D WITH_CUDA=OFF \
-D BUILD_TESTS=OFF \
-D BUILD_PERF_TESTS= OFF ..
```

#### Swap space size before compiling to add more virtual memory

It will enable OpenCV to compile with all four cores of the Raspberry PI without any memory issues.

Open your ```/etc/dphys-swapfile``` and then edit the ```CONF_SWAPSIZE``` variable

```bash
sudo nano /etc/dphys-swapfile
```

It will open the nano editor for editing the CONF_SWAPSIZE. Change it like below:

```bash
# set size to absolute value, leaving empty (default) then uses computed value
# you most likely don't want this, unless you have an special disk situation
# CONF_SWAPSIZE=100
CONF_SWAPSIZE=1024
```

Then save the changes you’ve made, press Ctrl + O. To exit nano, type Ctrl + X. If you ask nano to exit from a modified file, it will ask you if you want to save it. Just press N in case you don’t, or Y in case you do. It will then ask you for a filename. Just type it in and press Enter.
 
Then type the following lines to take it into effect

```bash
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

#### Compiling

Type the following command to compile it using 4 cores of pi

```bash
make -j4
```

#### Optional: Compile with a single core of Pi

If you face any error while compiling due to memory issue you can start the compilation again with only one core using the following command.

```bash
make clean
make
```

#### Install the build on Raspberry Pi

After the successful build install the build using the following command.

```bash
sudo make install
sudo ldconfig
```

#### Verify the OpenCV build

After running make install, OpenCV + Python bindings should be installed in usr/local/lib/python3.5/dist-packages or usr/local/lib/python3.5/site-packages.

You need to use the site-packages or dist-packages. Look where it has been created and use that site-packages or dist-packages. In my case it is in dist-packages.

Again, you can verify this with the ls command:

```bash
ls -l /usr/local/lib/python3.5/dist-packages/
```

Look for a name like cv2.so and if it is not there then look for a name like cv2.cpython-35m-arm-linux-gnueabihf.so (name starting with cv2. and ending with .so). It might happen due to some bugs in Python binding library for Python 3.

We need to rename cv2.cpython-35m-arm-linux-gnueabihf.so to cv2.so using the following command:

```bash
cd /usr/local/lib/python3.5/dist-packages/
sudo mv /usr/local/lib/python3.5/dist-packages/cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
```

#### Testing OpenCV 3.4.0 installation

```python
pi@raspberrypi:~ $ python3
Python 3.5.3 (default, Jan 19 2017, 14:11:04) 
[GCC 6.3.0 20170124] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'3.4.0'
```

#### Don’t forget to change your swap size back!

Open your ```/etc/dphys-swapfile```  and then edit the ```CONF_SWAPSIZE```  variable

```
sudo nano /etc/dphys-swapfile
```

It will open the nano editor for editing the CONF_SWAPSIZE. Change it like below:

```bash
# set size to absolute value, leaving empty (default) then uses computed value
# you most likely don't want this, unless you have an special disk situation
CONF_SWAPSIZE=100
# CONF_SWAPSIZE=1024
```

Then save the changes you’ve made, press Ctrl + O. To exit nano, type Ctrl + X. If you ask nano to exit from a modified file, it will ask you if you want to save it. Just press N in case you don’t, or Y in case you do. It will then ask you for a filename. Just type it in and press Enter.

Then type the following lines to take it into effect

```bash
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

### Account and key configurations

This app uses Azure Blob services, in order to access it you need to setup the account name and keys.
You need to create a file called ```config.ini``` and setup as follows:

```bash
; config.ini
[DEFAULT]
REMOTE_SERVER = "www.google.com"
ACCOUNT_NAME = ""
ACCOUNT_KEY = ""
CONTAINER_NAME = ""
QUEUE_NAME_AUDIO = "reaction-recording"
QUEUE_NAME_IMAGE = "reaction-imaging"
FRONT_END_APP = ""
```

Replace the following keys for each value:

- ```ACCOUNT_NAME```: Azure Blob account name
- ```ACCOUNT_KEY```: Azure blob account key from previo`us account name
- ```CONTAINER_NAME```: container name from previous account name responsible to receive audio and image files
- ```FRONT_END_APP```: URL of front-end app
  
The values of ```REMOTE_SERVER```, ```QUEUE_NAME_AUDIO``` and ```QUEUE_NAME_IMAGE``` can be changed, but take a look to the integrations in order the reflect the same names in other parts of the solution.

## How to use

For the first time you need to install the dependencies using the following command:

```bash
pip3 install -r requirements.txt
```

This app uses the desktop interface [Kivy](https://kivy.org/#home), check their site for addition information if you have trouble in the installation.

Once you have installed the dependencies, access the app using the shortcut ```meeting.Desktop```.

