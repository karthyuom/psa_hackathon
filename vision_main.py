'''
Created on 26 Sep 2016

@author: Karthick
@brief: Vision server module to detect people faces and text info. 
        Able to communicate with the robot to retrieve live camera stream
        Able to communicate with AWS server to recognize people via websocket
        Able to communicate with web-ui client via via websocket
'''


import argparse
import base64

from PIL import Image
from PIL import ImageDraw
import pickle

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
import time 

import os
import json
import sys
import urllib
import threading
from threading import Thread

from PIL import Image
import StringIO

from image_annotation import *

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
    
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
    
from twisted.python import log
from twisted.internet import reactor

from robot_action_handler import *


## Global declarations
g_robot_ip_addrs = "172.20.10.3"
g_robot_port = "5002"
g_snap_url = "http://"+g_robot_ip_addrs+":"+g_robot_port+"/snapshot"
g_enable_annotation = False #Enable this to get face, text annotaions from google vision API
g_frame_buf = None #TODO: Is this thread safe?
g_annotated_img = None #TODO: Is this thread safe?
g_people_name = ''
g_text_info = None


# [START get_vision_service]
DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials,
                           discoveryServiceUrl=DISCOVERY_URL)
# [END get_vision_service]


def detect_content(img_buf, max_results=4):
    """Uses the Vision API to detect contents such as faces, texts in the given image buffer.

    Args:
        img_buf: A image bytes object.

    Returns:
        An array of dicts with information about the faces in the picture.
    """

    batch_request = [{
        'image': {
            'content': base64.b64encode(img_buf).decode('UTF-8')
            },
        'features': [{
            'type': 'FACE_DETECTION',
            'maxResults': max_results,
            },
            {
            "type":"LABEL_DETECTION",
            "maxResults":10
            },
            {
               "type": "IMAGE_PROPERTIES",
               "maxResults": "10"
            },
            {
               "type": "TEXT_DETECTION",
               "maxResults": "20"
            }
             ]
        }]
# TEXT_DETECTION    Perform Optical Character Recognition (OCR) on text within the image
# LOGO_DETECTION    Detect company logos within the image
# SAFE_SEARCH_DETECTION    Determine image safe search properties on the image
# LANDMARK_DETECTION    Detect geographic landmarks within the image
# LABEL_DETECTION    Execute Image Content Analysis on the entire image and return
# FACE_DETECTION    Detect faces within the image
# IMAGE_PROPERTIES    Compute a set of properties about the image (such as the image's dominant colors)
    service = get_vision_service()

    request = service.images().annotate(body={
        'requests': batch_request,
        })
    response = request.execute()
    
    return response
# [END detect_content]


def resetGlobalEnv():
  global g_frame_buf, g_annotated_img, g_text_info, g_people_name
  g_frame_buf = None
  g_annotated_img = None
  g_text_info = None
  g_people_name = ''
  
  
def delay():
  pass
 
def retrieveLiveStream(stream_url):
  global g_frame_buf, g_annotated_img
  
  print("\nStart Retrieving live stream at %s..." % stream_url)
  stream = None
  try:
    stream = urllib.urlopen(stream_url)
  except:
    print"WARN: Stream not found."
    exit(0)
    
  bytes=''
  while True:
      if ((cv2.waitKey(1) == 27)):
          exit(0)
      startTime = time.time()
      bytes+=stream.read(1024*40)
      a = bytes.find('\xff\xd8')
      b = bytes.find('\xff\xd9')
      #print ('Stream reading took {0} second!'.format(time.time() - startTime))
      if a!=-1 and b!=-1:
          jpg = bytes[a:b+2]
          bytes= bytes[b+2:]
          frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
          g_frame_buf = frame
          response = None
          try:
            response = detect_content(jpg)
            t2 = time.time()
            print ('Content detection took {0} second!'.format(t2 - startTime))
          except:
            print'WARN: No response from google vision api!'
            continue
          
          #print(response['responses'][0])
          try:
            g_annotated_img = annotateImageLive(frame,response)
            #print g_annotated_img[1]
            #print ('Annotation took {0} second!'.format(time.time() - startTime))         
            save_image('temp_frame.jpg',frame)
            cv2.imshow('Original', frame)
            #cv2.imshow('Annotation', g_annotated_img[0])
            #t3 = time.time()
            #print ('Rendering took {0} second!'.format(t3 - t2))
          except:
            print 'WARN: Annotation failed!'
            continue
          #print ('Processing took {0} second!'.format(time.time() - startTime))
      timeout = threading.Timer(0.02,delay)
      timeout.start()   
      #time.sleep(1)
 
 
def getSnapshot(snap_url):
  global g_frame_buf, g_annotated_img, g_text_info, g_people_name
  resetGlobalEnv()
  
  print("\nGet snapshot at %s ..." % snap_url)
  
  startTime = time.time()
  req = None
  try:
    req = urllib.urlopen(snap_url)
  except:
    print"WARN: Snapshot is not found."
    return
  
  img_bytes = bytearray(req.read())
  arr = np.asarray(img_bytes, dtype=np.uint8)
  img = cv2.imdecode(arr, -1) # 'load it as it is'
  print ('Snapshot retrieval took {0} second!'.format(time.time() - startTime))
  t1 = time.time()
  
  g_frame_buf = img
  if not g_enable_annotation:
    print"WANR: Annotation has been disabled!"
    g_annotated_img = [g_frame_buf, "FACE"] #Snapshot will be sent for recognition only when the type is "FACE"
    return
  
  response = None
  try:
    response = detect_content(img_bytes)
    #print response
    t2 = time.time()
    print ('Content detection took {0} second!'.format(t2 - t1))
  except:
    print'WARN: No response from google vision api!'
    return
  try:
    g_annotated_img = annotateImageLive(img,response)   
    g_text_info = getTextInfo(response)
    if not g_text_info is None:
      playSound(g_text_info)
               
    #save_image('Snapshot.jpg',g_frame_buf)
    #save_image('Annotated.jpg',g_annotated_img[0])
    #cv2.imshow('Original', frame)
    #cv2.imshow('Annotation', g_annotated_img[0])
    t3 = time.time()
    print ('Annotation took {0} second!'.format(t3 - t2))
  except:
    print 'WARN: Annotation failed!'
    return
           
  #cv2.imshow('Snapshot',img)
  #if cv2.waitKey() & 0xff == 27: quit()


class VisionServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("Vision service socket connection open.")
         
        def renderFrame():
          if g_frame_buf is None:
            return
          img_buf = cv2.imencode('.png', g_frame_buf)[1].tostring()
          content = 'data:image/png;base64,' + \
                    urllib.quote(base64.b64encode(img_buf))
          msg = {
                  "type": "ORIGINAL",
                  "val":"Original frame rendering!",
                  "content": content
                }
          self.sendMessage(json.dumps(msg))
          self.factory.reactor.callLater(0.2, renderFrame)          
        
        #renderFrame()  
              
    def onMessage(self, payload, isBinary):
        raw = payload.decode('utf8')
        msg = json.loads(raw)
        print("Received {} message of length {}.".format(
            msg['type'], len(raw)))
                             
        if msg['type'] == "AUTO":
            if (g_annotated_img is None):
              msg = {
                      "type": "ANNOTATED",
                      "val": "Sorry, No annotation found!",
                      "content": "NULL"
                    }
              self.sendMessage(json.dumps(msg))
              return
              
            img_buf = cv2.imencode('.png', g_annotated_img[0])[1].tostring()
            val = ''
            if g_annotated_img[1] == 'FACE':
              val = g_people_name
              
            content = 'data:image/png;base64,' + \
                      urllib.quote(base64.b64encode(img_buf))
            msg = {
                    "type": "ANNOTATED",
                    "val":val,
                    "content": content
                  }
            self.sendMessage(json.dumps(msg))
                                       
        elif msg['type'] == "MANUALFACE":
            getSnapshot(g_snap_url)
            if g_annotated_img is None:
              return
              
            img_buf = cv2.imencode('.png', g_annotated_img[0])[1].tostring()
            val = ''
            if g_annotated_img[1] == 'FACE':
              val = g_people_name
              
            content = 'data:image/png;base64,' + \
                      urllib.quote(base64.b64encode(img_buf))
            msg = {
                    "type": "ANNOTATED",
                    "val":val,
                    "content": content
                  }
            self.sendMessage(json.dumps(msg))
            
        elif msg['type'] == "IDENTIFIED":
          #TODO: Add new person to AWS db
          pass
        else:
            print("WARN: Unknown message type: {}".format(msg['type']))

    def onClose(self, wasClean, code, reason):
        print("Vision service socket connection closed: {0}".format(reason))


class AWSClientProtocol(WebSocketClientProtocol):
    global g_annotated_img, g_frame_buf, g_people_name
    reply_received = 0
    start_processing = True
        
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("AWS Client connection open.")

        def register_faces(path_to_img,name):
            msg = {
                   'type':'ADD_PERSON',
                   'val':'NULL'
                   }
            msg['people_name'] = name
            with open(path_to_img, 'rb') as image:
                image_content = image.read()
                msg['val'] = base64.b64encode(image_content)
            print("Register person: "+ name)
            self.sendMessage(json.dumps(msg).encode('utf8'))
        
        def recognizeFace():
          if g_annotated_img is None:
            print("No frame found to recognize the people!")
            pass
          elif ((len(g_annotated_img) == 2) & (g_annotated_img[1] == "NONE")):
            print("Skip sending request to AWS...")
          elif ((len(g_annotated_img) == 2) & (g_annotated_img[1] == "TEXT")):
            print("Skip sending request to AWS...")
          elif ((len(g_annotated_img) == 2) & (g_annotated_img[1] == "FACE")):
            print("Send request to AWS to recognize the face...")
            msg = {
                   'type':'FRAME',
                   'val':'NULL'
                   }
            img_buf = cv2.imencode('.jpg', g_frame_buf)[1].tostring()
            msg['val'] = base64.b64encode(img_buf)
            self.sendMessage(json.dumps(msg).encode('utf8'))
            
          self.factory.reactor.callLater(7, recognizeFace)# Try sending request every 7 seconds
            
        ############ Register faces ############################################################## 
        #TODO: Uncomment if you need to register new faces   
        #register_face_dir = r"D:\Workspaces\eclipse-python\psa_hackathon\register_faces"
        #for img_f in os.listdir(register_face_dir):
          #name = str(img_f.split('.')[0])
          #print name
          #register_faces(os.path.join(register_face_dir,img_f), name)
        ##########################################################################################
        
        # Recognize people in the frame
        recognizeFace()
        
    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            raw = payload.decode('utf8')
            msg = json.loads(raw)
            #print("Received {} message of length {}.".format(msg['type'], raw))
            
            if (msg['type'] == "ADD_PERSON"):
              print("Successfully regsitered {0}".format(msg['people_name']))
            elif (msg['type'] == "FRAME"):
              if msg['people_name'] == "UNKNOWN":
                print("Sorry, I don't know who you are..!!")
                playSound("Sorry,   I don't  know   who you are")
              else:
                g_people_name = msg['people_name']
                print("Hi, {0}".format(g_people_name))
                playSound("Hi   "+g_people_name)
            
            resetGlobalEnv()#Reset all declaration after one snapshot
            
        if not self.start_processing:
            return

    def onClose(self, wasClean, code, reason):
        print("AWS Client connection closed: {0}".format(reason))
        
                   
def registerAWSClientConnection(public_ip):    
    log.startLogging(sys.stdout)
    factory = WebSocketClientFactory(u"ws://"+public_ip+":443")
    factory.protocol = AWSClientProtocol
    reactor.connectTCP(public_ip, 443, factory)
    reactor.run()
  
  
if __name__ == '__main__':

    ############ Initialize Robot action handler ####################
    status = initRobotAction(g_robot_ip_addrs, g_robot_port)
    if not status:
      exit(0)   
    ################################################################# 
    
    ############ Register live streaming thread #####################
    #stream_url = "http://"+g_robot_ip_addrs+":"+g_robot_port+"/vide_feed"
    #retr_th = Thread(target = retrieveLiveStream, args = (stream_url,))
    #retr_th.start()    
    ################################################################# 
    
    
    ############ Register AWS connection thread #####################
    public_ip= '52.220.132.34'
    vpn_ip = '172.31.30.131'    
    aws_th = Thread(target = registerAWSClientConnection, args = (public_ip,))
    aws_th.start()    
    ################################################################# 
    
    ########################## Server part ##########################
    #log.startLogging(sys.stdout)
    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = VisionServerProtocol
    reactor.listenTCP(9000, factory)
    reactor.run()    
    ########################## End Server ##########################
    
    ############ Test snapshot functionality #######################    
    #snap_url = 'http://answers.opencv.org/upfiles/logo_2.png'
    #snap_url = "http://172.20.10.6:5002/snapshot"
    #getSnapshot(g_snap_url)   
    #################################################################
    

