# Drone Circus
![gallery](https://user-images.githubusercontent.com/100842082/209651156-2c3cd627-aecb-4f25-bc12-530bbab7edde.png)


## What is Drone Circus?
Drone Circus is a front-end desktop application developed in Python and Tkinter that allows to control the drone platform in different ways (for example, with the voice or with body poses).
It is aimed at allowing the audience participating in the exhibition to interact with the drone in a safe and fun way.


## Installation
This video will help you in the process of installation. Basically you need to:
1. Clone the repo in your computer
2. Create a new Pycharm project with the downloaded codem using Pythion 3.7 interpreter
3. Install the requirements

To run the Drone Circus you need also to install and run the Autopilot service. Review the instructions of the corresponding repo.
Depending on the connection mode you will need also a mosquitto broker running in your computer. Review the information on connection modes in the main repo of the Drone Engineering Ecosystem.
Future versions of the Drone Circus may also need the Camera service or the Monitor.

## Demo
You can see here a demo on how to run the Drone Circus.
[Drone Circus in action](https://youtu.be/THVDBR6tlTI)

This is a summary of what you can see in the video:
1. Start the mosquitto broker in our local host. Look at the configuration file, that specifies that the broker will be listening in port 1884 (this is the broker that will be user as internal broker for on-board services) and in port 8000 using websockets (this is the broker that can be used as external broker).
2. Start mission planner. Then initiate the simulartor. You can see that before initiating the simulator we can chose the initial position of the drone that will be simulated. Then we go to the plan panel and select FENCE option. Here we can select three possible scenarios. In case A only an inclusion fence in the form of a rectangle is activated. In this case the drone cannot exit the area closed by the rectangle, but can move without restrictions inside the rectangle. Is case B there is and obstacle in the middle of the rectangle (a exclusion geofence). The drone cannot cross through this object. In case C threre are three obstables to be avoided. We chose case C. Do not forguet to write the scenario in the autopilot and to activate the geofence, as you can see in the video.
3. Run the Autopilot service. Note how do we specify two parameters for the Autopilot service. The first parameter is the connection mode, that can be local or gobal. We will use global. The second parameter is the operation mode, that can be simulation (our case) or prodution (when the Autopilot service is running on-board). The Autopilot servide will use the public broker at "broker.hivemq.com" as external broker. It also connect to the local broker "localhost:1884" that is used as internal broker, although this broker is not needed in this demo. You can see how the local broker indicates that the Autopilot service has been connected.
4. Run the Drone Circus. Note that it must use also "broker.hivemq.com" as external broker. The Drone Circus allows a varity of options to guide the drone in different ways. In this case we chose to guide with fingers. The number of fingers detected to by the laptop camera will determine the operation of the drone (go North, South, Est, West, Stop, Drop an object of Return home). You must choose the scenario, that obviously must be the same that was selected in Mission Planner (case C). Then you can practice the movements. The mission is to guide the drone to the baby, drop an object and return home.
5. Once you have enough practice, you must conect with the drone (the Mission Planner simulator). Note that you must select the connection mode, that in this case must be global (we decided that when we run the Autopilot service). Then the drone connects. You must arm and take off. Then you can guide the drone again but now you can see how we are moving the drone in the simulator, exactly in the same way we would do in production mode, with the real drone platform.
5. Finally, you can see other options such as guide the drone with your voice, your body poses or your face gestures.


## Installation and contribution
In order to run and contribute to this module you need Pythion 3.7. We recommend PyCharm as IDE for development.
To contribute to must follow the contribution protocol describen in the main repo of the Drone Engineering Ecosystem.
[![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-MainRepo-brightgreen.svg)](https://github.com/dronsEETAC/DroneEngineeringEcosystemDEE)


# Changes made here:

First a new MQTT client connected to the external broker on port 8000 is added to send messages to the Image Service.

The parameters of the game mode, the difficulty, the level and the image size will be sent on a JSON to the Image Service, before starting the practice inside the practice() function.

The loop on the practising() function is changed to send the video frames to the Image Service instead of detecting here the frames. The frames are stored on a list.

A new on_message_2() function is created to process the messages from the Image Service. It can receive the code and the video frames. When receiving the video frames it receives the index of the position of the image in the list and the vector of landmarks. It retrives the image and paints the landmarks on it.

New functions to paint the landmarks are also added, called draw_face(), draw_fingers() and draw_pose().

