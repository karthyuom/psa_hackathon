'''
Created on 26 Sep 2016

@author: Karthick
@brief: Annotate the given image. Able to annotate people faces or any text content.
'''

import pickle
import argparse
from utils_image import *

        
def annotateImage(orig_img, pickle_res_f_n):
  global g_img_scale
  
  h, w, ch = orig_img.shape
  new_img = cv2.resize(orig_img, (w/g_img_scale, h/g_img_scale))
  with open(pickle_res_f_n, 'rb') as handle:
        annot_data = pickle.load(handle)
        #print len(annot_data['responses'][0])
        #print annot_data
        response = annot_data['responses'][0]
        if ('faceAnnotations' in response):
          annotations = response['faceAnnotations']
          print('%s People found' % len(annotations))
          draw_face(new_img, annotations)
        elif ('textAnnotations' in response):
          annotations = response['textAnnotations']
          text_info = annotations[0]['description'].replace('\n', ' ')
          print('Text info found: %s' % text_info)
          new_img.fill(255)
          new_img = draw_color_text(new_img, text_info, (0,0,255))
                
  return new_img

def annotateImageLive(orig_img, pickle_response):
  global g_img_scale
  
  type = "NONE"
  h, w, ch = orig_img.shape
  new_img = cv2.resize(orig_img, (w/g_img_scale, h/g_img_scale))

  #print len(pickle_response['responses'][0])
  #print pickle_response
  response = pickle_response['responses'][0]
  if ('faceAnnotations' in response):
    annotations = response['faceAnnotations']
    print('%s People found' % len(annotations))
    draw_face(new_img, annotations)
    type = "FACE"
  elif ('textAnnotations' in response):
    annotations = response['textAnnotations']
    text_info = annotations[0]['description'].replace('\n', ' ')
    print('Text info found: %s' % text_info)
    new_img.fill(255)
    new_img = draw_color_text(new_img, text_info, (0,0,255))
    type = "TEXT"
  else:
    #return None#new_img
    type = "NONE"
                
  return [new_img, type]
  
if __name__ == '__main__':    
      parser = argparse.ArgumentParser(
        description='Annotate given image')
      parser.add_argument(
        'orig_image', help='The original image that need to be annotated.')
      parser.add_argument(
        'pickle', help='The original pickle data generated from google cloud.')
      args = parser.parse_args()
       
      orig_img = read_image(args.orig_image)
      annotated_img = annotateImage(orig_img, args.pickle)
      cv2.imshow('Original', orig_img)
      cv2.imshow('Annotation', annotated_img)
      cv2.waitKey()

  
  
    
        
        