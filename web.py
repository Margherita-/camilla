# -*- encoding: utf-8 -*-


# all the imports
from __future__ import with_statement
from contextlib import closing
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_pyfile('config.py', silent=False)

app.config.from_pyfile('DB_access.py', silent=False)

print app.config["HOST"]

db = MySQLdb.connect(
    host = app.config["HOST"], # your host, usually localhost
    user = app.config["USER"], # your username
    passwd = app.config["PASSWORD"], # your password
    db = app.config["DB"],
    use_unicode = True) # name of the data base


#main 
# mostra post
@app.route('/')
def show_entries():
    cur = db.cursor() 
    cur.execute("SELECT * FROM articoli")  
    entries = [dict(autor=row[1], title=row[3], text=row[4]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

# aggiungi post
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    cur = db.cursor()
    cur.execute('INSERT INTO articoli (titolo, contenuto, data) values (%s, %s, now())',
                 (request.form['title'], request.form['contenuto']))
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

# fai il login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/foto')
def show_foto():
    cur = db.cursor() 
    cur.execute("SELECT * FROM articoli")  
    entries = [dict(title=row[4], text=row[5]) for row in cur.fetchall()]
    return render_template('foto.html', entries=entries)
    
@app.route('/about')
def show_about():
    cur = db.cursor() 
    cur.execute("SELECT * FROM articoli")  
    entries = [dict(title=row[4], text=row[5]) for row in cur.fetchall()]
    return render_template('about.html', entries=entries)    

@app.route('/contatti')
def show_contatti():
    cur = db.cursor() 
    cur.execute("SELECT * FROM articoli")  
    entries = [dict(title=row[4], text=row[5]) for row in cur.fetchall()]
    return render_template('contatti.html', entries=entries)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="run the server with debug enabled",
                        action="store_true")
    args = parser.parse_args()
    if args.debug:
        print "verbosity turned on"
    
    app.debug = args.debug
    app.run(host='0.0.0.0')
