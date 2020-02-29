import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
import requests
from cv_bridge import CvBridge, CvBridgeError
from matplotlib import pyplot as plt
import sys
import os
import time

app = 0
command_publisher = rospy.Publisher(
    'obstacle_finder/cmd', String, queue_size=10)


def setup():

    global command_publisher
    rospy.init_node("obstacle_finder")
    print("Mission 1 begins")
    print("Take off!")
    command_publisher.publish("TAKEOFF")
    time.sleep(5)


def get_video():

    # Subscribes the video feed
    rospy.Subscriber('/bebop/image_raw', Image, callback)

    rospy.spin()

    cv2.destroyAllWindows()


def callback(data):

    global app
    global command_publisher

    rate = rospy.Rate(60)  # 60hz
    bridge = CvBridge()
    img = bridge.imgmsg_to_cv2(data, "bgr8")
    img = cv2.resize(img, (400, 224))

    # convert to HSV and extract saturation channel
    sat = cv2.cvtColor(img.copy(), cv2.COLOR_RGB2HSV)[:, :, 1]

    # threshold
    thresh = cv2.threshold(sat, 90, 150, 0)[1]

    # apply morphology close to fill interior regions in mask
    kernel = np.ones((29, 29), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    kernel = np.ones((31, 31), np.uint8)
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)

    # get contours (presumably only 1) and fit to simple polygon (quadrilateral)
    image, contours, hierarchy = cv2.findContours(
        morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
   # find the biggest countour (c) by the area
    if contours != 0 and app == 0:
        if not contours:
            command_publisher.publish("APPROACH")
            rate.sleep()
            cv2.putText(img, "CLOSE", (110, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            app = 1

        else:
            bigone = max(contours, key=cv2.contourArea) if max else None
            area = cv2.contourArea(bigone)
            if area > 1000 and app == 0:
                x, y, w, h = cv2.boundingRect(bigone)
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(img, "Obstacle", (x+w/2, y-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                obs_area = w*h
                print(obs_area)

                if obs_area <= 30000 and app == 0 and obs_area > 3000:

                    command_publisher.publish("GO")
                    rate.sleep()
                    cv2.putText(
                        img, "GO", (160, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                if obs_area <= 3000:
                    command_publisher.publish("APPROACH")
                    rate.sleep()
                    cv2.putText(img, "CLOSE", (110, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                    app = 1

                if obs_area > 30000 and app == 0:
                    command_publisher.publish("STOP")
                    rate.sleep()
                    cv2.putText(img, "CLOSE", (110, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

                    app = 1

                if app == 1:
                    command_publisher.publish("APPROACH")
                    rate.sleep()
                    cv2.putText(img, "FINAL", (110, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    else:
        command_publisher.publish("APPROACH")
        rate.sleep()
        cv2.putText(img, "FINAL", (110, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    if app == 1:
        cv2.putText(img, "FINAL", (110, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    # Display image
    cv2.imshow("IMAGE", img)

    cv2.waitKey(1)


if __name__ == '__main__':

    setup()
    try:
        get_video()

    except rospy.ROSInterruptException:
        pass
