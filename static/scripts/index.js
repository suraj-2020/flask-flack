var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
var curr_room = "General Room";
var user = '';
function joinroom(room) {
    socket.emit("join", { "user": user, "room": curr_room });
}

function leaveroom(room) {
    document.querySelector('.chat').innerHTML = '';
    socket.emit('leave', { "user": user, "room": curr_room })
}

function func(p) {
    var room = p.innerHTML;
    if (room == curr_room) {
        alert("Already in the same room ");
    }
    else {
        leaveroom(curr_room);
        curr_room = room;
        joinroom(curr_room);
    }
}

function differ(msg) {
    l = []
    msg1 = ""
    flag = 0
    msg2 = ""
    for (i = 0; i < msg.length; i++) {
        if (msg[i] == ":")
            flag = 1
        if (flag == 0)
            msg1 += msg[i]
        else if (flag == 1)
            msg2 += msg[i]
    }
    msg3= msg2.slice(-19)
    msg2=msg2.substr(1,msg2.length-20)
    l.push(msg1)
    l.push(msg2)
    l.push(msg3)
    return l;
}

function add_msg(msg){
    siz=msg.length
    if(msg[siz-1]=="t")
    {
        const p = document.createElement('p');
        p.innerHTML = msg;
        p.style.color="white";
        document.querySelector('.chat').append(p);
    }
    else
    {
        const div = document.createElement('div');
        div.className = "container";
        var x= differ(msg);
        console.log(x);
        const p2 = document.createElement('p');
        p2.innerHTML = x[0];
        p2.style.textShadow = "2px 2px 5px red";
        const p = document.createElement('p');
        p.innerHTML = x[1];
        p.style.color="white";
        const span=document.createElement('span');
        span.innerHTML = x[2];
        span.style.display="block"
        span.style.textAlign="right";
        div.append(p2);
        div.append(p);
        div.append(span);
        document.querySelector('.chat').append(div);
    }
}

document.addEventListener('DOMContentLoaded', () => {

    
    socket.on('connect', () => {
        socket.send();
    })

    socket.on('first', data => {
        data_print = "Welcome " + data + ", chat away!";
        document.querySelector('#name').innerHTML = data_print;
        user = data;
        joinroom(curr_room);
    })

    socket.on('join_message', lis => {
        if (document.querySelector('.chat').innerHTML == '') {
            for (i = 0; i < lis.length; i++) {
                add_msg(lis[i]);
            }
        }
        else {
            add_msg(lis[(lis.length - 1)]);
        }
    })

    socket.on('leave_message', msg => {
        const p = document.createElement('p');
        p.innerHTML = msg;
        p.style.color="white";
        document.querySelector('.chat').append(p);
    })

    socket.on('message_display', msg => {
      add_msg(msg);
    })

    socket.on('room_exists', data => {
        alert(data);
    })

    socket.on('room_created', data => {
        const p = document.createElement('p');
        p.innerHTML = data;
        p.setAttribute("id", data);
        p.setAttribute("onclick", "func(this)");
        document.querySelector('.rooms').append(p);
    })

    document.querySelector('#cb1').onclick = () => {
        let m = document.querySelector('#ctext').value;
        m = user + ":\n" + m;
        socket.emit("send_chat", { "msg": m, "room": curr_room });
        document.querySelector('#ctext').value='';//clear input field
    }

    document.querySelector('#rb1').onclick = () => {
        let m = document.querySelector('#rtext').value;
        //alert(m);
        socket.emit("create_room", { "msg": m });
        document.querySelector('#rtext').value='';
    }

    let msg = document.querySelector('#rtext');
    msg.addEventListener('keyup', event=>{
        event.preventDefault();
        if(event.keyCode === 13){
            document.querySelector('#rb1').click();
        }
    })

    let msg2 = document.querySelector('#ctext');
    msg2.addEventListener('keyup', event=>{
        event.preventDefault();
        if(event.keyCode === 13){
            document.querySelector('#cb1').click();
        }
    })

})