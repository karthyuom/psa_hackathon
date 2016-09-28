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

import urllib
from threading import Thread

from PIL import Image
import StringIO

from image_annotation import *


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
  global g_frame_buf
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
      if cv2.waitKey(1) ==27:
          exit(0)
      bytes+=stream.read(32)
      a = bytes.find('\xff\xd8')
      b = bytes.find('\xff\xd9')
      if a!=-1 and b!=-1:
          jpg = bytes[a:b+2]
          bytes= bytes[b+2:]
          frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
          #g_frame_buf.append(frame)
          #cv2.imshow('Live Streaming',frame)
          #count += 1
          #save_image('live_stream_frame' + str(count) + '.jpg',frame)
          #save_image('live_stream_frame.jpg',frame)
          #temp_frame = g_frame_buf.pop(0)
          response = detect_content(jpg)
          #print(response['responses'][0])
          annotated_img = annotateImageLive(frame,response)
          if annotated_img == None:
            continue
          #cv2.imshow('Original', frame)
          cv2.imshow('Annotation', annotated_img)
          
      #time.sleep(1)

def processFrame(dataURL,):
  head = "data:image/jpeg;base64,"
  assert(dataURL.startswith(head))
  imgdata = base64.b64decode(dataURL[len(head):])
  imgF = StringIO.StringIO()
  imgF.write(imgdata)
  imgF.seek(0)
  img = Image.open(imgF)     

if __name__ == '__main__':
    startTime = time.time()

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
    #stream_url = "http://172.20.10.2:5002/video_feed"
    stream_url = "http://172.20.10.6:5002/video_feed"
    retr_th = Thread(target = retrieveLiveStream, args = (stream_url,))
    retr_th.start()
    #process_th = Thread(target = processLiveStream, args = ())
    #process_th.start()
    #process_th.join()
    
    #processFrame(stream_url)
    
    #retrieveLiveStream(stream_url)
    # Your code here !
    #print ('The script took {0} second !'.format(time.time() - startTime))
