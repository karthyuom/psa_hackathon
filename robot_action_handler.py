'''
Created on 3 Oct 2016

@author: Karthick
@brief: Provides functionalities to execute set of actions on robot
'''

import json
import requests


g_action_url = None
g_headers = {'Content-type': 'application/json'}
g_action_lists = ["FORWARD", "STOP", "TURNLEFT", "TURNRIGHT", "BACKFORWARD", "FORWARD_SLOW"]


def initRobotAction(robot_ip_addrss, port):
  global g_action_url
  g_action_url = "http://"+robot_ip_addrss+":"+port+"/actionlist"
  
  text_to_play = "Hi     i am the robot"
  status = playSound(text_to_play)
  return status
  
def playSound(text):
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : text}
  cmd_txt = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_txt, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True
  
def showActions():
  print g_action_lists

def moveForward():
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : "FORWARD"}
  cmd_fwrd = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_fwrd, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True

def stop():
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : "STOP"}
  cmd_stop = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_stop, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True

def turnLeft():
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : "TURNLEFT"}
  cmd_left = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_left, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True

def turnRight():
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : "TURNRIGHT"}
  cmd_right = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_right, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True

def moveBackward():
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : "BACKFORWARD"}
  cmd_back = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_back, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True

def moveForwardSlow():
  if (g_action_url is None):
    print("WARN:initRobotAction() before execute any actions")
    return False
  
  data = {"action" : "FORWARD_SLOW"}
  cmd_fwd_slow = json.dumps(data)
  try:
    response = requests.post(g_action_url, data=cmd_fwd_slow, headers=g_headers)
  except:
    print("WARN: Robot failed to respond")
    return False
  
  return True


if __name__ == '__main__':
  
  ##Test all action commands
  robot_ip_add = "172.20.10.3"
  port = "5002"
  initRobotAction(robot_ip_add, port)
  showActions()
  text_to_play = "This is a text command to play."
  status = playSound(text_to_play)
  status = moveForward()
  #moveBackward()
  #moveForwardSlow()
  #turnLeft()
  #turnRight()
  #stop()
  

