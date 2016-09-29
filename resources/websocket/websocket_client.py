'''
Created on 28 Sep 2016

@author: samzhang
'''
#!/usr/bin/python

#!/usr/bin/python

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import sys
import base64
import os
from twisted.python import log
from twisted.internet import reactor

class MyClientProtocol(WebSocketClientProtocol):
    
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

        # start sending messages every second ..
        hello()
        
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


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    public_ip= '52.220.132.34'
    vpn_ip = '172.31.30.131'
#     factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory = WebSocketClientFactory(u"ws://"+public_ip)
    factory.protocol = MyClientProtocol

    reactor.connectTCP(public_ip, 80, factory)
#     reactor.connectTCP("172.31.30.131", 9000, factory)
    reactor.run()
    
    
