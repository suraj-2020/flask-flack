import os

from flask import Flask,render_template,request,session,redirect,url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from time import ctime

# running on local the second parameter won't be required
app = Flask(__name__,static_url_path='/static')
# mysecret is the key which will be used to encrypt the session variable
app.config["SECRET_KEY"] = "mysecrets!!!"
socketio = SocketIO(app)

# python3 -m venv env
# 1) automatic clear input field after submit
# 2) when enter hit should be submit
# 3) color scheme 


users={}
rooms={"General Room":[]}

# This stores session in a cookie even after the browser is close
@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route("/login",methods=["GET","POST"])
def login():
    if session.get('user'):
        return render_template("index.html",rooms=rooms)
    if request.method=="GET":
        return render_template("test_login.html")
    else:
        name=request.form.get('name')
        passw=request.form.get('pass')
        if name in users:
            if users[name]==passw:
                session['user']=name
                return redirect(url_for('chat'))
        message="Invalid Username or Password"
        return render_template("test_login.html",message=message)


@app.route("/signup",methods=["GET","POST"])
def signup():
    if session.get('user'):
        return render_template("index.html",rooms=rooms)
    if request.method=="GET":
        return render_template("test_signup.html")
    else:
        name=request.form.get('name')
        passw=request.form.get('pass')
        if not name.strip():#checking for blank username and passwords
            message="Empty Username not allowed"
            return render_template('test_signup.html',message=message)
        if not passw.strip():
            message="Empty Password not allowed"
            return render_template('test_signup.html',message=message)
        if name in users:
            message="username taken, try another name"
            return render_template('test_signup.html',message=message)
        users[name]=passw
        session['user']=name
        return redirect(url_for('chat'))

#route for chatting
@app.route("/chat")
def chat():
    return render_template('index.html',rooms=rooms)

#session.clear() clears all the session created, session.pop(session_name) can be used for removing specific session
@app.route("/logout")
def logout():
    session.clear()
    return render_template("test_login.html")

# this is the route when used socket.send on js as send cannot be named, message coming from connect 
@socketio.on('message')
def first():
    mess=session['user']
    emit('first',mess)

#from the dictionary sending the chats of the specific room , coming from emit join , which is called by onclick submit(message) event listener
@socketio.on('join')
def joins(data):
    user=data['user']
    room=data['room']
    join_room(room)
    message=user+" has entered the chat"
    rooms[room].append(message)
    lis=[]
    for i in rooms[room]:
        lis.append(i)
    emit("join_message",lis, room=room)

#on leaving the room, leave_room is socketio predefined function. room is compulsary paramete(obvious reason)
@socketio.on('leave')
def joins(data):
    user=data['user']
    room=data['room']
    leave_room(room)
    message=user+" has left the chat"
    emit("leave_message", message, room=room)

# appending name,message and time in single variable which is then differentiated in js
@socketio.on('send_chat')
def msg(mdata):
    message=mdata['msg']
    room=mdata['room']
    time=ctime()#always length 24
    time=time[:-5]#dropping year
    message=message+time
    rooms[room].append(message)
    emit("message_display",message,room=room)


@socketio.on('create_room')
def create(data):
    name=data['msg']
    if name in rooms:
        emit('room_exists','room name already taken')
    else:
        rooms[name]=[]
        emit('room_created',name, broadcast = True)

# while running on local run socketio
# app.run wass use for deployment
if __name__ == '__main__':
    socketio.run(app,debug=True)
    #app.run()