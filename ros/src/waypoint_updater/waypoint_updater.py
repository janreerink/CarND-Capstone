#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from scipy.spatial import KDTree
import math
from std_msgs.msg import Int32
import numpy as np
'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number
MAX_DECEL = 1.0

class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')


        # TODO: Add other member variables you need below
        #init vars
        self.pose = None
        self.base_waypoints = None
        self.waypoints_2d = None
        self.waypoint_tree = None
        self.stopline_wp_idx = -1
        #rospy.spin()
        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below
        rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)
        #rospy.Subscriber('/obstacle_waypoint', Lane, self.waypoints_obs)


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)


        self.loop()

    def loop(self):
        #as shown in walkthrough
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            if self.pose and self.base_waypoints:
                #closest_waypoints_idx = self.get_closest_waypoint_idx()
                #self.publish_waypoints_old(closest_waypoints_idx) #no traffic light detection
                self.publish_waypoints()
            rate.sleep()
            
    def publish_waypoints_old(self, closest_idx):
        #as shown in walkthrough
        lane = Lane()
        lane.header = self.base_waypoints.header
        lane.waypoints = self.base_waypoints.waypoints[closest_idx: closest_idx + LOOKAHEAD_WPS]
        self.final_waypoints_pub.publish(lane)
        
    def publish_waypoints(self):
        #final_lane = self.generate_lane()
        lane = Lane()
        lane.header = self.base_waypoints.header
        closest_idx = self.get_closest_waypoint_idx()
        farthest_idx = closest_idx + LOOKAHEAD_WPS
        waypoints_range = self.base_waypoints.waypoints[closest_idx:farthest_idx]
        if self.stopline_wp_idx == -1 or (self.stopline_wp_idx >= farthest_idx): #no traffic light detected or too far away
            #rospy.logwarn("no red lights detected or out of range")
            lane.waypoints = waypoints_range
        else:
            #rospy.loginfo("detected light idx %s", self.stopline_wp_idx)
            lane.waypoints = self.decelerate_waypoints(waypoints_range, closest_idx) #traffic light in range: change WPs
        #self.final_waypoints_pub.publish(final_lane)
        self.final_waypoints_pub.publish(lane)
       
        
    def generate_lane(self): #obsolete
        lane = Lane()
        lane.header = self.base_waypoints.header
        
        closest_idx = self.get_closest_waypoint_idx()
        farthest_idx = closest_idx + LOOKAHEAD_WPS
        waypoints_range = self.base_waypoints.waypoints[closest_idx:farthest_idx]
        #print('--------------')
        #print(self.base_waypoints.waypoints[0])
        #print(closest_idx)
        #print(farthest_idx)
        #print(waypoints_range[0])
        #print('--------------')
        if self.stopline_wp_idx == -1 or (self.stopline_wp_idx >= farthest_idx): #no traffic light detected or too far away
            #rospy.info("no red lights detected or out of range")
            lane.waypoints = waypoints_range
        else:
            #rospy.info("detected light idx %s", self.stopline_wp_idx)
            lane.waypoints = self.decelerate_waypoints(waypoints_range, closest_idx) #traffic light in range: change WPs
        return lane

    def decelerate_waypoints(self, waypoints, closest_idx):
        temp = []
        for idx, wp in enumerate(waypoints):
            #make new wp, keep position
            p = Waypoint()
            p.pose = wp.pose 
            
            #change associated wp velocity
            stop_idx = max(self.stopline_wp_idx - closest_idx - 2, 0) #to adjust car front with stopline
            dist = self.distance(waypoints, idx, stop_idx)
            vel = math.sqrt(2 * MAX_DECEL * dist)
            if vel < 1:
                vel = 0
            p.twist.twist.linear.x = min(vel, wp.twist.twist.linear.x)
            temp.append(p)
        return temp
            
    def get_closest_waypoint_idx(self):
        #as shown in walkthrough
        x = self.pose.pose.position.x
        y = self.pose.pose.position.y
        closest_idx = self.waypoint_tree.query([x,y], 1)[1]
        
        closest_coord = self.waypoints_2d[closest_idx]
        prev_coord = self.waypoints_2d[closest_idx-1]
        
        cl_vect = np.array(closest_coord)
        prev_vect = np.array(prev_coord)
        pos_vect = np.array([x,y])
        
        val = np.dot(cl_vect - prev_vect , pos_vect - cl_vect)
        
        if val > 0:
            closest_idx = (closest_idx +1 ) % len(self.waypoints_2d)
        return closest_idx
       
        
    
        
    
    def pose_cb(self, msg):
        #store current position
        self.pose = msg
        pass

    def waypoints_cb(self, waypoints):
        #store incoming waypoints as object attribute
        self.base_waypoints = waypoints
        if not self.waypoints_2d:
            self.waypoints_2d = [[waypoint.pose.pose.position.x, waypoint.pose.pose.position.y] for waypoint in waypoints.waypoints]
            self.waypoint_tree = KDTree(self.waypoints_2d)
        pass

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        #rospy.loginfo("traffic light msg %s", msg)
        self.stopline_wp_idx = msg.data
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist
        


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
