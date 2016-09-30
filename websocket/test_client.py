###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import cv2
import numpy as np
import base64
from base64 import b64encode
from PIL import Image
import StringIO

class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        def hello():
            self.sendMessage(u"Hello, world!".encode('utf8'))
            self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            self.factory.reactor.callLater(1, hello)
        def requestFrame():
            req_msg = {
                        "type": "AUTO",
                        "val": "NULL"
                      }
            self.sendMessage(json.dumps(req_msg))
            self.factory.reactor.callLater(1, requestFrame)

        # start sending messages every second ..
        #hello()
        requestFrame()

    def onMessage(self, payload, isBinary):
        raw = payload.decode('utf8')
        msg = json.loads(raw)
        print("Received {} message of length {}.".format(
            msg['type'], len(raw)))
        if msg['type'] == "ORIGINAL_FRAME":
          print("Content: {0}".format(msg['content']))
        elif msg['type'] == "ANNOTATED_FRAME":
          #print("Content: {0}".format(msg['content']))    
          head = "data:image/png;base64,"
          assert(msg['content'].startswith(head))
          imgdata = base64.b64decode(msg['content'][len(head):])
          imgF = StringIO.StringIO()
          imgF.write(imgdata)
          imgF.seek(0)
          img = Image.open(imgF)

          #buf = np.fliplr(np.asarray(img))
          #rgbFrame = np.zeros((300, 400, 3), dtype=np.uint8)
          #rgbFrame[:, :, 0] = buf[:, :, 2]
          #rgbFrame[:, :, 1] = buf[:, :, 1]
          #rgbFrame[:, :, 2] = buf[:, :, 0]

          #cv2.write('frame_recvd.png', rgbFrame)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyClientProtocol

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()