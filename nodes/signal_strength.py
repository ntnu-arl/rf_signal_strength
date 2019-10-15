#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int32, Float32
import os
import iperf3

invalid = -9999

def get_signal_strength(timer_event):
	global wifi_device_name, level_sig_strength_pub, link_sig_strength_pub, noise_sig_strength_pub, invalid
	link_msg = Int32()
	level_msg = Int32()
	noise_msg = Int32()
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


def get_bandwidth(timer_event):
	global bandwidth_pub, iperf_server_addr
	try:
		client = iperf3.Client()
		client.duration = 1
		client.server_hostname = iperf_server_addr
		client.port = 5201
		print("Running Iperf3")
		result = client.run()
		print("Iperf3 Complete")

		tx_mbps_pub.publish(result.sent_Mbps)
		rx_mbps_pub.publish(result.received_Mbps)
		re_tx_pub.publish(result.retransmits)
	except:
		tx_mbps_pub.publish(-1.0)
		rx_mbps_pub.publish(-1.0)
		re_tx_pub.publish(-1.0)


rospy.init_node('signal_strength', anonymous=True)
wifi_device_name = rospy.get_param("/signal_strength/wifi_device_name", default="wlp4s0")
iperf_server_addr = rospy.get_param("/signal_strength/iperf_server_addr", default="192.168.0.40")
rospy.loginfo("Getting Signal Strength on Device : %s", wifi_device_name)

level_sig_strength_pub = rospy.Publisher("signal_strength/level", Int32, queue_size=10)
link_sig_strength_pub = rospy.Publisher("signal_strength/link", Int32, queue_size=10)
noise_sig_strength_pub = rospy.Publisher("signal_strength/noise", Int32, queue_size=10)
rx_mbps_pub = rospy.Publisher("signal_strength/rx_mbps", Float32, queue_size=10)
tx_mbps_pub = rospy.Publisher("signal_strength/tx_mbps", Float32, queue_size=10)
re_tx_pub = rospy.Publisher("signal_strength/re_tx", Float32, queue_size=10)
signal_strength_timer = rospy.Timer(rospy.Duration(0.25),get_signal_strength)
bandwidth_timer = rospy.Timer(rospy.Duration(2.0),get_bandwidth)

rospy.spin()