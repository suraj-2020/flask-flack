import os

from flask import Flask,render_template,request,session
from flask_socketio import SocketIO, emit, join_room, leave_room
from time import ctime

app = Flask(__name__,static_url_path="",static_folder="project2/static",template_folder="project2/template")
app.config["SECRET_KEY"] = os.environ.get('SECRET')
socketio = SocketIO(app)

# python3 -m venv env
# 1) automatic clear input field after submit
# 2) when enter hit should be submit
# 3) color scheme 


users={}
rooms={"General Room":[]}

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
                return render_template('index.html',rooms=rooms)
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
        if not name.strip():
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
        return render_template('index.html',rooms=rooms)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("test_login.html")

@socketio.on('message')
def first():
    mess=session['user']
    emit('first',mess)


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

@socketio.on('leave')
def joins(data):
    user=data['user']
    room=data['room']
    leave_room(room)
    message=user+" has left the chat"
    emit("leave_message", message, room=room)


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

if __name__ == '__main__':
    app.run()