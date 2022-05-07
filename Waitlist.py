from flask import Flask, render_template, abort, redirect, request, jsonify
from sqlite3 import connect

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/host')
def host_page():
    return render_template("Host.html")


@app.route('/host', methods=['post'])
def add_wait():
    name = request.form.get('name')

    if not name:
        return redirect('/host')

    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Room(name) VALUES (?)", [name])

    room_id = cursor.lastrowid

    conn.commit()

    print(room_id)

    return redirect("/waitlist/%s/host" % room_id)


@app.route("/waitlist/<int:room_id>/host")
def index_host(room_id):
    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.execute("SELECT name FROM Room WHERE id LIKE ?", [room_id])
    name = cursor.fetchone()[0]
    cursor = conn.execute(
        "SELECT priority,nickname  FROM Users WHERE room_id = ? AND priority IS NOT NULL ORDER BY priority ASC ",
        [room_id])
    waitlist = cursor.fetchall()
    return render_template("Hostview.html", waitlist=waitlist, room_id=room_id, name=name)


@app.route("/waitlist/<room_id>/host/end")
def end_room(room_id):
    conn = connect("./Databases/rooms.sqlite")
    conn.execute("DELETE FROM Room WHERE id LIKE ?", [room_id])
    conn.execute("DELETE FROM Users WHERE room_id LIKE ?", [room_id])
    return redirect('/')


@app.route('/join')
def join_page():
    return render_template("Join.html")


@app.route('/join', methods=['post'])
def join():

    nickname = request.form.get('nickname')
    room_id1 = request.form.get('room_id')
    room_id = int(room_id1)

    if not nickname or not room_id:
        return redirect('/join')
    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.cursor()
    number = conn.execute("SELECT * FROM Room WHERE id LIKE ?", [room_id])
    if not number:
        return redirect('/join')
    cursor.execute("INSERT INTO Users(nickname, room_id) VALUES (?, ?)", [nickname, room_id])
    conn.commit()
    cursor = conn.execute("SELECT id FROM Users WHERE nickname LIKE ?", [nickname])
    user_id = cursor.fetchone()[0]
    return redirect(f"/waitlist/{room_id}/{user_id}")


@app.route('/waitlist/<int:room_id>/table')
def get_wait(room_id):
    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.execute(
        "SELECT id,nickname  FROM Users WHERE room_id = ? AND priority IS NOT NULL ORDER BY priority ASC ",
        [room_id])
    waitlist = cursor.fetchall()
    return jsonify(waitlist)


@app.route('/waitlist/<int:room_id>/host/view')
def participants_get(room_id):
    # todo: get the table of people in your room which is has a priority and order asc
    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.execute("SELECT id, nickname, priority FROM Users WHERE room_id = ?", [room_id])
    participants = cursor.fetchall()
    print(participants)
    return render_template("participants.html", room_id=room_id, participants=participants, id = id)


@app.route('/waitlist/<int:room_id>/<int:user_id>/signup', methods=['POST', 'GET'])
def sign_up(user_id, room_id,):
    # TODO: get users find the last person and list priority +1 and make you cant sign up twice
    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.execute("SELECT MAX(priority) FROM Users WHERE room_id = ?", [room_id])
    u_pri = cursor.fetchone()[0]
    if u_pri:
        u_pri += 1
    else:
        u_pri = 1

    conn.execute("UPDATE Users SET priority = ? WHERE id = ?", [u_pri, user_id])
    conn.commit()
    return redirect(f'/waitlist/{room_id}/{user_id}')


@app.route('/waitlist/<int:room_id>/<int:user_id>/leave')
def leave(room_id, user_id):
    conn = connect("./Databases/rooms.sqlite")
    conn.execute("DELETE FROM Users WHERE id LIKE ?", [user_id])
    conn.commit()
    return redirect('/')


@app.route("/waitlist/<int:room_id>/<int:user_id>/")
def index_user(room_id, user_id):
    conn = connect("./Databases/rooms.sqlite")
    cursor = conn.execute("SELECT name FROM Room WHERE id LIKE ?", [room_id])
    name = cursor.fetchone()[0]
    cursor = conn.execute(
        "SELECT priority,nickname  FROM Users WHERE room_id = ? AND priority IS NOT NULL ORDER BY priority ASC ",
        [room_id])
    waitlist = cursor.fetchall()

    return render_template("Userview.html", waitlist=waitlist, room_id=room_id, name=name, user_id = user_id)


@app.route("/waitlist/<int:room_id>/host/<int:user_id>/delete")
def delete_user(room_id, user_id):
    conn = connect("./Databases/rooms.sqlite")
    conn.execute("DELETE FROM Users WHERE id LIKE ?", [user_id])
    conn.commit()
    return redirect(f'/waitlist/{room_id}/host')
#
@app.route("/waitlist/<int:room_id>/host/<int:user_id>/delprior", methods=['POST', 'GET'] )
def del_prior2(user_id, room_id):
    conn = connect("./Databases/rooms.sqlite")
    conn.execute("UPDATE Users SET priority = NULL  WHERE id = ?", [user_id])
    conn.commit()
    return redirect(f'/waitlist/{room_id}/host')

@app.route("/waitlist/<int:room_id>/<int:user_id>/delprior", methods=['POST', 'GET'] )
def del_prior1(user_id, room_id):
    conn = connect("./Databases/rooms.sqlite")
    conn.execute("UPDATE Users SET priority = NULL  WHERE id = ?", [user_id])
    conn.commit()
    return redirect(f'/waitlist/{room_id}/{user_id}')

app.run(host="0.0.0.0", port=8082, debug=False)
