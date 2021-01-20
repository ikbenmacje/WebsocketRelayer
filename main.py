from flask import Flask, render_template
from flask_socketio import SocketIO
from flask import request
from pythonosc import udp_client, osc_message_builder, osc_bundle_builder
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app, ping_timeout=10, ping_interval=5, cors_allowed_origins="*")

# OSC
port = 8888
OSCclients = {}
OSCclients[0] = udp_client.SimpleUDPClient('127.0.01', port) # local debug 
OSCclients[1] = udp_client.SimpleUDPClient('192.168.1.5', port) # local debug 

# track number of clients connected (currently including conductor)
clients = 0

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@app.route('/')
def sessions():
    return render_template('session.html')

@app.route('/conductor')
def conductor():
    return render_template('conductor.html')

@socketio.on('connect')
def on_connect():
    print("Client connect event")
    global clients
    clients += 1
    socketio.emit('connect', {'event': 'Connected', 'clientid': request.sid });

@socketio.on('disconnect')
def on_disconnect():
    global clients
    clients -= 1
    socketio.emit('disconnect', {'event': 'Disconnected', 'clientid': request.sid });
    print( 'Client disconnected', request.sid )

@socketio.on('message_event')
def on_message_event(msg):
    print('received message: {}'.format(msg))
    socketio.emit("message_event", { 'clientid': request.sid, 'message': msg });

    
    # got setRGB color message
    if(msg == "setRandomColor"):

        for i in range(len(OSCclients)):
            
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)

            OSCclients[i].send_message("/colorRGB", [r,g,b])



    '''
    # OSC test
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    message = osc_message_builder.OscMessageBuilder(address='/colorRGB')
    message.add_arg(random.randint(0,255))
    message.add_arg(random.randint(0,255))
    message.add_arg(random.randint(0,255))


    #bundle.add_content(message.build())
    #OSCclients[0].send_message("/colorRGB", [100, 220,50])

    # Debug
    OSCclients[0].send(message.build())
    # Real clietn
    OSCclients[1].send(message.build())
    '''
    



@socketio.on_error_default
def default_error_handler(e):
    print("######### ERROR HANDLER #########")
    print(e)
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)
    print("######### END ERROR HANDLER #####")


if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', port=7000, debug=True)
