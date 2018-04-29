[//]: # (Image References)
[image0]: ./imgs/final-project-ros-graph-v2.png "architecture"

This is the project repo for the final project of the Udacity Self-Driving Car Nanodegree: Programming a Real Self-Driving Car. For more information about the project, see the project introduction [here](https://classroom.udacity.com/nanodegrees/nd013/parts/6047fe34-d93c-4f50-8336-b70ef10cb4b2/modules/e1a23b06-329a-4684-a717-ad476f0d8dff/lessons/462c933d-9f24-42d3-8bdc-a08a5fc866e4/concepts/5ab4b122-83e6-436d-850f-9f4d26627fd9).

Please use **one** of the two installation options, either native **or** docker installation.

### Project walkthrough
The goal of this project is to implement several ROS nodes to make a simulated car complete several tracks in the provided simulator.

The following pictures illustrates the architecture of the ROS implementation:
![alt text][iamge0]


#### Partial Waypoint node
As suggested in the lessons, as a first step the update_waypoints node was partially implemented in order for the simulator to be useful for development of other nodes.
This node is supposed to pubhlish a list of waypoints with respective target velocities, taking into account obstacles and traffic lights. However, initially it was sufficient
for the nodes to subscribe to several topics and publish its own topic of updated waypoints.
As shown in the walkthrough, a KDTree is used to find the closest waypoints and return a subset of the base waypoint list after checking if the closest waypoints is in front or behind the vehicle.

#### DBW node
The next step was to implement the drive-by-wire node, which receives twist commands, current velocity and the status of the dbw-mode (auto or manual). Depending on these inputs, the dbw-node should
publish control inputs for acceleration and steering. Twist commands are published based on waypoints and associated velocities.
THe dbw node subscribes to get dbw mode, the current velocity and target linear and angular velocities. These values are sent to a controller, which provides suitable throttle, brake and steering values to
be published.
The controller uses the standard PID and lowpass functions provided in the starter code. 

#### traffic light detection node
This node takes the position of traffic lights, camera images to determine the light's color, the car's position and the list of base waypoints. If a red traffic light is close to the car the waypoint
is published to a list of traffic waypoints. These are later used to modify the listof waypoints so that the car decelerates and stops at the traffic light line.
For classification of images the Google Object Detection API was used, as shown here:
https://becominghuman.ai/traffic-light-detection-tensorflow-api-c75fdbadac62
https://github.com/mkoehnke/CarND-Capstone-TrafficLightDetection


#### Waypoint updater part 2
With the traffic light detection working, the waypoint updater can utilize information on nearby traffic light states to change target velocities for waypoints so that the car slows down and stops at red lights.
In case of a red light detected in range, the current list of waypoints is replaced by a list of identical waypoints with changed speed settings, aiming to smoothly decelerate to get to 0 speed at the
stopping line.




### Native Installation

* Be sure that your workstation is running Ubuntu 16.04 Xenial Xerus or Ubuntu 14.04 Trusty Tahir. [Ubuntu downloads can be found here](https://www.ubuntu.com/download/desktop).
* If using a Virtual Machine to install Ubuntu, use the following configuration as minimum:
  * 2 CPU
  * 2 GB system memory
  * 25 GB of free hard drive space

  The Udacity provided virtual machine has ROS and Dataspeed DBW already installed, so you can skip the next two steps if you are using this.

* Follow these instructions to install ROS
  * [ROS Kinetic](http://wiki.ros.org/kinetic/Installation/Ubuntu) if you have Ubuntu 16.04.
  * [ROS Indigo](http://wiki.ros.org/indigo/Installation/Ubuntu) if you have Ubuntu 14.04.
* [Dataspeed DBW](https://bitbucket.org/DataspeedInc/dbw_mkz_ros)
  * Use this option to install the SDK on a workstation that already has ROS installed: [One Line SDK Install (binary)](https://bitbucket.org/DataspeedInc/dbw_mkz_ros/src/81e63fcc335d7b64139d7482017d6a97b405e250/ROS_SETUP.md?fileviewer=file-view-default)
* Download the [Udacity Simulator](https://github.com/udacity/CarND-Capstone/releases).

### Docker Installation
[Install Docker](https://docs.docker.com/engine/installation/)

Build the docker container
```bash
docker build . -t capstone
```

Run the docker file
```bash
docker run -p 4567:4567 -v $PWD:/capstone -v /tmp/log:/root/.ros/ --rm -it capstone
```

### Port Forwarding
To set up port forwarding, please refer to the [instructions from term 2](https://classroom.udacity.com/nanodegrees/nd013/parts/40f38239-66b6-46ec-ae68-03afd8a601c8/modules/0949fca6-b379-42af-a919-ee50aa304e6a/lessons/f758c44c-5e40-4e01-93b5-1a82aa4e044f/concepts/16cf4a78-4fc7-49e1-8621-3450ca938b77)

### Usage

1. Clone the project repository
```bash
git clone https://github.com/udacity/CarND-Capstone.git
```

2. Install python dependencies
```bash
cd CarND-Capstone
pip install -r requirements.txt
```
3. Make and run styx
```bash
cd ros
catkin_make
source devel/setup.sh
roslaunch launch/styx.launch
```
4. Run the simulator

### Real world testing
1. Download [training bag](https://s3-us-west-1.amazonaws.com/udacity-selfdrivingcar/traffic_light_bag_file.zip) that was recorded on the Udacity self-driving car.
2. Unzip the file
```bash
unzip traffic_light_bag_file.zip
```
3. Play the bag file
```bash
rosbag play -l traffic_light_bag_file/traffic_light_training.bag
```
4. Launch your project in site mode
```bash
cd CarND-Capstone/ros
roslaunch launch/site.launch
```
5. Confirm that traffic light detection works on real life images
