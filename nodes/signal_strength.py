#!/usr/bin/env python
import rospy
from std_msgs.msg import Int16
import os


invalid = -9999

def get_signal_strength(timer_event):
	global wifi_device_name, level_sig_strength_pub, link_sig_strength_pub, noise_sig_strength_pub, invalid
	link_msg = Int16()
	level_msg = Int16()
	noise_msg = Int16()
	try:
		call_result = os.popen("cat  /proc/net/wireless").read()
		if wifi_device_name in call_result:
			start = call_result.find(wifi_device_name) + len(wifi_device_name) + 1
			strength_string = call_result[start:]
			val_list = strength_string.split()
			link_msg.data  = int(val_list[1].replace('.', ''))
			level_msg.data = int(val_list[2].replace('.', ''))
			noise_msg.data = int(val_list[3].replace('.', ''))
		else:
			rospy.logwarn_throttle(1.0, "Signal Strength Pkg : Failed to get wifi device, check wifi device name!")
			link_msg.data  = invalid
			level_msg.data = invalid
			noise_msg.data = invalid
		level_sig_strength_pub.publish(level_msg)
		link_sig_strength_pub.publish(link_msg)
		noise_sig_strength_pub.publish(noise_msg)
	except:
		rospy.logwarn_throttle(1.0, "Signal Strength Pkg : Failed to get wifi info!")
		link_msg.data  = invalid
		level_msg.data = invalid
		noise_msg.data = invalid
		level_sig_strength_pub.publish(level_msg)
		link_sig_strength_pub.publish(link_msg)
		noise_sig_strength_pub.publish(noise_msg)


rospy.init_node('signal_strength', anonymous=True)
wifi_device_name = rospy.get_param("wifi_device_name", default="wlp4s0")
rospy.loginfo("Getting Signal Strength on Device : %s", wifi_device_name)

level_sig_strength_pub = rospy.Publisher("signal_strength/level", Int16, queue_size=10)
link_sig_strength_pub = rospy.Publisher("signal_strength/link", Int16, queue_size=10)
noise_sig_strength_pub = rospy.Publisher("signal_strength/noise", Int16, queue_size=10)
signal_strength_timer = rospy.Timer(rospy.Duration(0.25),get_signal_strength)

rospy.spin()