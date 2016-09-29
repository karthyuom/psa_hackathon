#!/usr/bin/env python

# Copyright 2015 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Draws squares around faces in the given image."""

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


# [START get_vision_service]
DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'


def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials,
                           discoveryServiceUrl=DISCOVERY_URL)
# [END get_vision_service]


# [START detect_face]
def detect_face(face_file, max_results=4):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of dicts with information about the faces in the picture.
    """
    image_content = face_file.read()
    batch_request = [{
        'image': {
            'content': base64.b64encode(image_content).decode('UTF-8')
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
    
    # Store data (serialize)
    #with open('response.pickle', 'wb') as handle:
        #pickle.dump(response, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Load data (deserialize)
    #with open('response.pickle', 'rb') as handle:
        #unserialized_data = pickle.load(handle)

    return response
# [END detect_face]

def detect_content(img_file, max_results=4):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of dicts with information about the faces in the picture.
    """
    #image_content = img_file.read()
    #image_content = read_image(img_file)
    batch_request = [{
        'image': {
            'content': base64.b64encode(img_file).decode('UTF-8')
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
    
    # Store data (serialize)
    #with open('response.pickle', 'wb') as handle:
        #pickle.dump(response, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Load data (deserialize)
    #with open('response.pickle', 'rb') as handle:
        #unserialized_data = pickle.load(handle)

    return response
# [END detect_content]


# [START highlight_faces]
def highlight_faces(image, faces, output_filename):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
      output_filename: the name of the image file to be created, where the faces
          have polygons drawn around them.
    """
    im = Image.open(image)
    draw = ImageDraw.Draw(im)

    for face in faces:
        box = [(v.get('x', 0.0), v.get('y', 0.0)) for v in face['fdBoundingPoly']['vertices']]
        draw.line(box + [box[0]], width=5, fill='#00ff00')

    del draw
    im.save(output_filename)
# [END highlight_faces]


# [START main]
def main(input_filename, output_filename, max_results):
    with open(input_filename, 'rb') as image:
        response = detect_face(image, max_results)
        orig_img = read_image(input_filename)
        annotated_img = annotateImageLive(orig_img,response)
        cv2.imshow('Original', orig_img)
        cv2.imshow('Annotation', annotated_img)
        cv2.waitKey()
        #print('Found %s face%s' % (len(faces), '' if len(faces) == 1 else 's'))

        #print('Writing to file %s' % output_filename)
        # Reset the file pointer, so we can read the file again
        #image.seek(0)
        #highlight_faces(image, faces, output_filename)
# [END main]

g_frame_buf = []
g_annotated_img = None

def processLiveStream():
  global g_frame_buf
  print("\nStart processing live stream...")
  while True:
    if cv2.waitKey(1) ==27:
          return
    print len(g_frame_buf)
    if len(g_frame_buf) == 0:
      #print("WARN: Empty stream buffer")
      continue
    temp_frame = g_frame_buf.pop(0)
    response = detect_content(temp_frame, 4)
    #print response
    annotated_img = annotateImageLive(temp_frame,response)
    if annotated_img == None:
      continue
    #cv2.imshow('Original', frame)
    save_image('annotated_img.jpg',annotated_img)
    #cv2.imshow('Annotation', annotated_img)
    time.sleep(0.5)
  
  
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
  #count = 0
  while True:
      if ((cv2.waitKey(1) == 27)):
          exit(0)
      startTime = time.time()
      bytes+=stream.read(1024)
      a = bytes.find('\xff\xd8')
      b = bytes.find('\xff\xd9')
      #print ('Stream reading took {0} second!'.format(time.time() - startTime))
      if a!=-1 and b!=-1:
          jpg = bytes[a:b+2]
          bytes= bytes[b+2:]
          frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
          #print ('Decoding took {0} second!'.format(time.time() - startTime))
          #g_frame_buf.append(frame)
          #cv2.imshow('Live Streaming',frame)
          #count += 1
          #save_image('live_stream_frame' + str(count) + '.jpg',frame)
          #save_image('live_stream_frame.jpg',frame)
          #temp_frame = g_frame_buf.pop(0)
          response = None
          try:
            response = detect_content(jpg)
            t2 = time.time()
            print ('Content detection took {0} second!'.format(t2 - startTime))
          except:
            print'WARN: No response found for the frame.'
            continue
          
          #print(response['responses'][0])
          try:
            g_annotated_img = annotateImageLive(frame,response)
            #print g_annotated_img[1]
            #print ('Annotation took {0} second!'.format(time.time() - startTime))
            if g_annotated_img is None:
              continue
            #cv2.imshow('Original', frame)
            #cv2.imshow('Annotation', annotated_img)
            #t3 = time.time()
            #print ('Rendering took {0} second!'.format(t3 - t2))
          except:
            print 'WARN: Annotation failed!'
            continue
          #print ('Processing took {0} second!'.format(time.time() - startTime))
          
      #time.sleep(1)


class VisionServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        
    def onMessage(self, payload, isBinary):
        raw = payload.decode('utf8')
        msg = json.loads(raw)
        print("Received {} message of length {}.".format(
            msg['type'], len(raw)))
        
        if msg['type'] == "REQ_FRAME":
            #self.sendFrame()
            #save_image('temp_frame.jpg', g_annotated_img)
            if (g_annotated_img is None):
              msg = {
                      "type": "ORIGINAL_FRAME",
                      "content": "Sorry, No annotation found!"
                    }
              self.sendMessage(json.dumps(msg))
            else:          
                #self.sendMessage('From:[Vision module]=> Found annotation!', False)
                #img_data = StringIO.StringIO()
                #g_annotated_img
                #plt.savefig(img_data, format='png')
                #img_data.seek(0)
                img_buf = cv2.imencode('.png', g_annotated_img)[1].tostring()
                print img_buf
                content = 'data:image/png;base64,' + \
                          urllib.quote(base64.b64encode(img_buf))
                msg = {
                        "type": "ANNOTATED_FRAME",
                        "content": content
                      }
                self.sendMessage(json.dumps(msg))
        else:
            print("WARN: Unknown message type: {}".format(msg['type']))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class AWSClientProtocol(WebSocketClientProtocol):
    
    img_path = r'C:\Users\samzhang\Downloads\face_detection'
    imgs = ["mei4.JPG",
"mei3.JPG",
"mei2.JPG",
"eva2.JPG",
"sam1.JPG",
"sam2.JPG",
"eva3.JPG",
"eva4.JPG",
"eva5.JPG",
"eva6.JPG",
"eva1.JPG",
"sam3.JPG",
"mei1.JPG"
            ]
    reply_received = 0
    
    start_processing = True
    
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        def hello():
            msg = {
                   'type':'NEW FACE',
                   'val':'NULL'
                   }
#             self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
#             for img in self.imgs:
            #img = self.imgs[0]
            img = "sam2.JPG"
#             img = 'mei1.JPG'
#             msg['type'] = 'ADD_PERSON'

            with open(os.path.join(r"D:\Workspaces\eclipse-python\psa_hackathon\resources\websocket", img), 'rb') as image:
#             with open(r'C:\Users\samzhang\Downloads\face_detection\eva_img\DSC_9477.JPG', 'rb') as image:
                image_content = image.read()
                msg['val'] = base64.b64encode(image_content)
            print("getting data for face "+ self.imgs[self.reply_received])
            msg['type'] = 'FRAME'
#             msg['people_name'] = 'xiao mei'    
            self.sendMessage(json.dumps(msg).encode('utf8'))
        
        def recognizeFace():
          if g_annotated_img is None:
            pass
          elif ((len(g_annotated_img) == 2) & (g_annotated_img[1] == "TEXT")):
            print("Send request to AWS to recognize the face...")
          self.factory.reactor.callLater(1, recognizeFace)
            
        # start sending messages every second ..
        #hello()
        recognizeFace()
        
    def onMessage(self, payload, isBinary):
        msg = {
        'type':'NEW FACE',
        'val':'NULL'
        }
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
            
        if not self.start_processing:
            return
        if self.reply_received < len(self.imgs)-1:
            self.reply_received = self.reply_received +1;
        else:
            self.reply_received = 0 
        img = "sam2.JPG"
        with open(os.path.join(r"D:\Workspaces\eclipse-python\psa_hackathon\resources\websocket", img), 'rb') as image:
        #             with open(r'C:\Users\samzhang\Downloads\face_detection\eva_img\DSC_9477.JPG', 'rb') as image:
            image_content = image.read()
            msg['val'] = base64.b64encode(image_content)
        print("getting data for face "+ self.imgs[self.reply_received])
        msg['type'] = 'FRAME'
        msg['people_name'] = 'Eva Wang'    
        self.sendMessage(json.dumps(msg).encode('utf8'))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        
                   
def registerAWSClientConnection(public_ip):
    log.startLogging(sys.stdout)
    
    factory = WebSocketClientFactory(u"ws://"+public_ip)
    factory.protocol = AWSClientProtocol

    reactor.connectTCP(public_ip, 80, factory)
    reactor.run()
  
  
if __name__ == '__main__':
#    startTime = time.time()

#     parser = argparse.ArgumentParser(
#         description='Detects faces in the given image.')
#     # parser.add_argument(
#         # '--input_image', default='1.jpg',
#         # help='the image you\'d like to detect faces in.')
#     parser.add_argument(
#         'input_image', help='the image you\'d like to detect faces in.')
#     parser.add_argument(
#         '--out', dest='output', default='out.jpg',
#         help='the name of the output file.')
#     parser.add_argument(
#         '--max-results', dest='max_results', default=4,
#         help='the max results of face detection.')
#     args = parser.parse_args()
# 
#     main(args.input_image, args.output, args.max_results)


    ############ Register live streaming thread #####################
    
    #stream_url = "http://172.20.10.2:5002/video_feed"
    stream_url = "http://172.20.10.6:5002/video_feed"
    retr_th = Thread(target = retrieveLiveStream, args = (stream_url,))
    retr_th.start()   
    
    ################################################################# 
    
    
    ############ Register AWS connection thread #####################
    public_ip= '52.220.132.34'
    vpn_ip = '172.31.30.131'    
    aws_th = Thread(target = registerAWSClientConnection, args = (public_ip,))
    aws_th.start()
    
    ################################################################# 
    
    ########################## Server part ##########################
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = VisionServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()
    
    ########################## End Server ##########################
    
    
    #process_th = Thread(target = processLiveStream, args = ())
    #process_th.start()
    #process_th.join()
    
    #processFrame(stream_url)
    
    #retrieveLiveStream(stream_url)
    # Your code here !
    #print ('The script took {0} second !'.format(time.time() - startTime))
