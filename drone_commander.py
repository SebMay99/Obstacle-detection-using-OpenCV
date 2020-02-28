import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from std_msgs.msg import Empty
import sys
import os
import rospy

last_command = ""


def abort(data):
    print("Emergency!")
    os._exit(1)


def commander(data):

    global last_command

    #rospy.Subscriber("/obstacle_finder/cmd", String, commander).unregister()

    rate = rospy.Rate(5)  # 5hz

    #print("Received :", data)
    # print(type(data))

    command = data.data
    print(command)
    time = 0.6
    final_time = 1

    takeoff_publisher = rospy.Publisher(
        'bebop/takeoff', Empty, queue_size=1)

    landing_publisher = rospy.Publisher(
        'bebop/land', Empty, queue_size=1)

    movement_publisher = rospy.Publisher(
        'bebop/cmd_vel', Twist, queue_size=1)

    if command == "GO":

        print("Forward")
        counter = 0.0
        movement_cmd = Twist()
        while not rospy.is_shutdown():
            movement_cmd.linear.x = 0.1
            movement_cmd.linear.y = 0
            movement_cmd.linear.z = 0
            movement_cmd.angular.x = 0
            movement_cmd.angular.y = 0
            movement_cmd.angular.z = 0
            counter += 0.2
            movement_publisher.publish(movement_cmd)
            rate.sleep()
            print(counter)
            if counter >= time:
                #command = ""
                break

    if command == "STOP":

        print("Stop")
        counter = 0.0
        movement_cmd = Twist()
        while not rospy.is_shutdown():
            movement_cmd.linear.x = 0
            movement_cmd.linear.y = 0
            movement_cmd.linear.z = 0
            movement_cmd.angular.x = 0
            movement_cmd.angular.y = 0
            movement_cmd.angular.z = 0
            counter += 0.2
            movement_publisher.publish(movement_cmd)
            rate.sleep()
            if counter >= time:
                #command = ""
                break

    if command == "APPROACH":

        print("Close")
        counter = 0.0
        movement_cmd = Twist()
        while not rospy.is_shutdown():
            movement_cmd.linear.x = -0.1
            movement_cmd.linear.y = 0
            movement_cmd.linear.z = 0
            movement_cmd.angular.x = 0
            movement_cmd.angular.y = 0
            movement_cmd.angular.z = 0
            counter += 0.2
            movement_publisher.publish(movement_cmd)
            rate.sleep()
            if counter >= final_time:
                movement_cmd = Empty()
                while not rospy.is_shutdown():
                    landing_publisher.publish(movement_cmd)
                    counter += 0.2
                    rate.sleep()
                    if counter >= time:
                        print("Landing!")
                        os._exit(1)

    if command == 'TAKEOFF':

        counter = 0.0
        movement_cmd = Empty()
        while not rospy.is_shutdown():
            takeoff_publisher.publish(movement_cmd)
            counter += 0.05
            rate.sleep()
            if counter >= time:
                #command = ""
                break


def setup():
    rospy.init_node("bebop_commander")
    rospy.Subscriber('chatter', String, abort)
    rospy.Subscriber('obstacle_finder/cmd', String,
                     commander, queue_size=1, buff_size=2**12)
    rate = rospy.Rate(5)  # 5hz

    rospy.spin()


if __name__ == '__main__':

    try:
        setup()

    except rospy.ROSInterruptException:
        pass
