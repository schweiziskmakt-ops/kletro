from flask import render_template, request, session, redirect, abort, url_for, flash, current_app
from my_server import app
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from my_server.db_handler import create_connection
import time
from datetime import datetime
import os
from uuid import uuid4
from datetime import timedelta

app.permanent_session_lifetime = timedelta(minutes=30)  

def get_db_connection():
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    return conn

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

def normalize_pair(a: int, b: int):
    if a < b:
        return a, b
    return b, a

def get_friend_relation(conn, user_a, user_b):
    if user_a == user_b:
        return None

    u1, u2 = normalize_pair(user_a, user_b)

    return conn.execute(
        "SELECT status, requested_by FROM friendships WHERE user_id1=? AND user_id2=?",
        (u1, u2)
    ).fetchone()



@app.route('/')
def start():
    return render_template('start.html')


@app.route('/home')
def home():
    with get_db_connection() as conn:
        posts = conn.execute("""
            SELECT
                posts.*,
                users.username AS author_username
            FROM posts
            JOIN users ON users.id = posts.author_id
            ORDER BY posts.id DESC
        """).fetchall()

    return render_template('home.html', posts=posts, username=session.get("username"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Fyll i användarnamn och lösenord.")
            return render_template('login.html')

        with get_db_connection() as conn:
            user = conn.execute(
                'SELECT id, username, password_hash FROM users WHERE username = ?',
                (username,)
            ).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session.permanent = True
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))

        flash("Inloggning misslyckades!",'error')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/users', methods=['POST', 'GET'])
def list_users():
    if not session.get('logged_in'):
        abort(401)
    else:
        if request.method == 'POST':
            pass
            
        
        with get_db_connection() as conn:
            usersearch = request.values.get('search', '').strip()
            sql = "SELECT username FROM users WHERE username LIKE ?"
            users = conn.execute(sql, ("%" + usersearch + "%", )).fetchall()
        
    return render_template('listusers.html', users=users, username=session.get("username"))

@app.route('/users/<username>')
def user_posts(username):
    if not session.get('logged_in'):
        abort(401)

    with get_db_connection() as conn:
        profile_user = conn.execute(
            "SELECT id, username FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not profile_user:
            abort(404)

        posts = conn.execute(
            "SELECT * FROM posts WHERE author_id = ? ORDER BY id DESC",
            (profile_user["id"],)
        ).fetchall()

        me_id = session["user_id"]
        other_id = profile_user["id"]

        relation = get_friend_relation(conn, me_id, other_id)

    return render_template('listposts.html',
        posts=posts,
        user=profile_user,
        username=session.get("username"),
        relation=relation)


@app.route("/create", methods=["GET", "POST"])
def create_post():
    if not session.get("logged_in"):
        abort(401)
    if request.method == "GET":
        return render_template("create.html")

    username = session["username"]
    titel = request.form.get("titel", "")
    content = request.form.get("content", "")
    grades = request.form.get("grades", "")
    time = datetime.now().date()
    image = request.files.get("image")
    image_filename = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[1].lower()
        image_filename = f"{uuid4().hex}.{ext}"
        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        image.save(os.path.join(upload_dir, image_filename))

    conn = get_db_connection()
    user_id = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()["id"]
    conn.execute(
        "INSERT INTO posts (author_id, titel, content, grades, time , image_filename) VALUES (?, ?, ?, ?, ? , ?)",
        (user_id, titel, content, grades, time, image_filename),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/createlead", methods=["GET", "POST"])
def create_post_lead():
    if not session.get("logged_in"):
        abort(401)
    if request.method == "GET":
        return render_template("createlead.html")

    username = session["username"]
    titel = request.form.get("titel")
    content = request.form.get("content", "")
    grades = request.form.get("grades", "")
    time = datetime.now().date()
    image = request.files.get("image")
    image_filename = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[1].lower()
        image_filename = f"{uuid4().hex}.{ext}"
        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        image.save(os.path.join(upload_dir, image_filename))

    conn = get_db_connection()
    user_id = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()["id"]
    conn.execute(
        "INSERT INTO posts (author_id, titel, content, grades, time , image_filename) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, titel, content, grades, time, image_filename),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))




@app.route('/villkor', methods=['GET', 'POST'])
def villkor():
    return render_template('villkor.html')




@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if not session.get('logged_in'):
        abort(401)
    else:
        username = session['username']

        now = datetime.now()
        hour = now.hour
        if hour < 12:
            greeting = "God Morgon"
        elif hour < 18:
            greeting = "God Eftermiddag"
        else:
            greeting = "God Kväll"

        monthly_data = [
            ("Aug", "6B"),
            ("Sep", "6C"),
            ("Okt", "6B+"),  
            ("Nov", "6C+"),
            ("Dec", "6C+"),   
            ("Jan", "7A"),   
        ]

        FONT_GRADES = {
            "6A": 4, "6A+": 5,
            "6B": 6, "6B+": 7,
            "6C": 8, "6C+": 9,
            "7A": 10
        }

        FONT_GRADES_REVERSE = {v: k for k, v in FONT_GRADES.items()}

        labels = [row[0] for row in monthly_data]
        values = [FONT_GRADES[row[1]] for row in monthly_data]
        
        with get_db_connection() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()

            if not user:
                abort(404)

            posts = conn.execute(
                'SELECT * FROM posts WHERE author_id = ?',
                (user['id'],)
            ).fetchall()
            
            friend_count = conn.execute("""
    SELECT COUNT(*) AS count
    FROM friendships
    WHERE status = 'accepted'
      AND (user_id1 = ? OR user_id2 = ?)
""", (user["id"], user["id"])).fetchone()["count"]

    return render_template(
        'profilepage.html',
        greeting=greeting,
        username=username,
        labels=labels,
        values=values,
        grade_map=FONT_GRADES_REVERSE,
        posts=posts,
        friend_count=friend_count
    )


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if session.get('logged_in'):
        flash('You are already logged in.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        passwordrepeat = request.form.get('passwordrepeat', '')
        if not password == passwordrepeat:
            flash('Lösenordet måste vara samma')
            return render_template('signup.html')
        if not username or not password:
            flash('Username and password are required.')
            return render_template('signup.html')

        password_hash = generate_password_hash(password)

        try:
            with get_db_connection() as conn:
                conn.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, password_hash)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already taken.')
            return render_template('signup.html')

        flash('Account created. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')



@app.route("/creategroup", methods=['GET','POST'])
def create_group():
    if not session.get('logged_in'):
        abort(401)
    if request.method == "GET":
        return render_template("creategroup.html")


    username = session["username"]
    titel = request.form.get("titel", "")
    content = request.form.get("content", "")
    privacy = request.form.get("privacy", "")
    image = request.files.get("image")
    image_filename = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[1].lower()
        image_filename = f"{uuid4().hex}.{ext}"
        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        image.save(os.path.join(upload_dir, image_filename))

    conn = get_db_connection()
    user_id = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()["id"]
    conn.execute(
        "INSERT INTO groups (author_id, titel, content, privacy, image_filename) VALUES (?, ?, ?, ?, ?)",
        (user_id, titel, content, privacy, image_filename),
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('groups'))

@app.route("/groups")
def groups():
    if not session.get('logged_in'):
        abort(401)
    with get_db_connection() as conn:
        groups = conn.execute(
            'SELECT * FROM groups'
        ).fetchall()
    
    return render_template('groups.html', groups=groups)

@app.route("/groups/<int:group_id>")
def group_page(group_id):
    if not session.get('logged_in'):
        abort(401)

    user_id = session["user_id"]

    with get_db_connection() as conn:
        group = conn.execute("""
            SELECT g.*,
                   u.username AS author_username
            FROM groups g
            JOIN users u ON u.id = g.author_id
            WHERE g.id = ?
        """, (group_id,)).fetchone()

        is_member = conn.execute("""
            SELECT 1
            FROM group_members
            WHERE group_id = ? AND user_id = ?
            LIMIT 1
            """, (group_id, user_id)).fetchone() is not None
        
        member_count = conn.execute("""
            SELECT COUNT(*) AS count
            FROM group_members
            WHERE group_id = ?


        """, (group_id,)).fetchone()["count"]
        members = conn.execute("""
            SELECT u.id, u.username
            FROM group_members gm
            JOIN users u ON u.id = gm.user_id
            WHERE gm.group_id = ?
            ORDER BY u.username COLLATE NOCASE
        """, (group_id,)).fetchall()

    return render_template("groupspage.html", group=group, is_member=is_member,member_count=member_count, members=members)


@app.route("/groups/<int:group_id>/join", methods=['POST']) 
def groups_join(group_id):
    if not session.get('logged_in'):
            abort(401)

    user_id = session['user_id']
        
    with get_db_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO group_members (group_id, user_id)
            VALUES (?, ?)

        """,( group_id, user_id))
        conn.commit()
        

        
    return redirect(url_for("group_page", group_id=group_id))


@app.route("/friends/request/<int:user_id>", methods=["POST"])
def friend_request(user_id):
    if not session.get("logged_in"):
        abort(401)

    me = session["user_id"]
    if me == user_id:
        abort(400)

    u1, u2 = normalize_pair(me, user_id)

    with get_db_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO friendships (user_id1, user_id2, status, requested_by)
            VALUES (?, ?, 'pending', ?)
        """, (u1, u2, me))
        conn.commit()

    return redirect(url_for("home"))




@app.route("/friends/accept/<int:user_id>", methods=["POST"])
def friend_accept(user_id):
    if not session.get("logged_in"):
        abort(401)

    me = session["user_id"]
    u1, u2 = normalize_pair(me, user_id)

    with get_db_connection() as conn:
        rel = conn.execute("""
            SELECT status, requested_by
            FROM friendships
            WHERE user_id1=? AND user_id2=?
        """, (u1, u2)).fetchone()

        if not rel or rel["status"] != "pending":
            abort(404)

        if rel["requested_by"] == me:
            abort(403)

        conn.execute("""
            UPDATE friendships
            SET status='accepted'
            WHERE user_id1=? AND user_id2=?
        """, (u1, u2))
        conn.commit()
        

    return redirect(url_for("home"))


@app.route("/friends/remove/<int:user_id>", methods=["POST"])
def friend_remove(user_id):
    if not session.get("logged_in"):
        abort(401)

    me = session["user_id"]
    u1, u2 = normalize_pair(me, user_id)

    with get_db_connection() as conn:
        conn.execute("DELETE FROM friendships WHERE user_id1=? AND user_id2=?", (u1, u2))
        conn.commit()

    return redirect(url_for("home"))


@app.route('/about')
def about():
    return render_template("about.html")