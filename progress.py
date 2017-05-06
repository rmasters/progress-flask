from flask import Flask, request, session, g, url_for, abort, render_template, flash, redirect
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from datetime import datetime

import config

app = Flask(__name__)
app.config.from_object(config)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
#try to connect to the database. 
#if it hasn't been initialized, do that
    try:
        g.db = connect_db()
    except sqlite3.OperationalError:
        g.db = connect_db()
        init_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/")
def countdowns():
    cur = g.db.execute('select name, deadline, created from deadline')
    entries = [dict(
        name=row[0],
        deadline=row[1],
        created=row[2],
        timeleft=datetime.now()-datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')) for row in cur.fetchall()]
    return render_template('countdowns.html', entries=entries)

@app.route("/add", methods=['POST'])
def add_deadline():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("insert into deadline (name, deadline, created) values (?, ?, 'now')",
                 [request.form['name'], request.form['deadline']])
    g.db.commit()
    flash('Deadline added')
    return redirect(url_for('countdowns'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('countdowns'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('countdowns'))

if __name__ == "__main__":
    #init_db()
    app.run(host='0.0.0.0', port=9999)
