'''
Created on 27 Sep 2016

@author: samzhang
'''
'''
Created on 27 Sep 2016

@author: samzhang
'''
from flask import Flask, render_template, Response
from flask_restful import reqparse, abort, Api, Resource
import argparse
import time 


# emulated camera
from camera_pi import Camera

app = Flask(__name__)
api = Api(app)

from Queue import Queue

# actionQueue = Queue(maxsize=0)
# 
# actionQueue.put()

TODOS = {
    'todo1': {'action': 'build an API'},
    'todo2': {'action': '?????'},
    'todo3': {'action': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Action {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('action')


# Action
# shows a single todo item and lets you delete a todo item
class Action(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    ##change/update exiting action. 
    def put(self, todo_id):
        args = parser.parse_args()
        action = {'action': args['action']}
        print "action edited" + action
        
        TODOS[todo_id] = action
        return action, 201


# ActionList
# shows a list of all todos, and lets you POST to add new actions
class ActionList(Resource):
    def get(self):
        return TODOS

    #add new action to the action list
    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'action': args['action']}
        print 'new action added to the queue: '+args['action']
        
        # remember to remove the action from the queue.
        return TODOS[todo_id], 201

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

## Actually setup the Api resource routing here
##
api.add_resource(ActionList, '/actionlist')
api.add_resource(Action, '/actionlist/<todo_id>')

if __name__ == '__main__':
    startTime = time.time()

    initparser = argparse.ArgumentParser(
        description='video stream server.')
    initparser .add_argument(
        '--port', dest='port', default='5002',
        help='the port for this service to be running.')
    initargs = initparser .parse_args()

    # Your code here !
    app.run(host='0.0.0.0', port=int(initargs.port), debug=True, threaded=True)
    print ('The script took {0} second !'.format(time.time() - startTime))
