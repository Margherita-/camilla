# -*- encoding: utf-8 -*-


# all the imports
from __future__ import with_statement
import os, sys
from contextlib import closing
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from get_photo import give_me_photos, save_photos

# create our little application :)
app = Flask(__name__)

app.config.from_pyfile('config.py', silent=False)
app.config.from_pyfile('DB_access.py', silent=False)
app.config.from_pyfile('Flickr_config.py', silent=False)

#trova dove si trova il file corrente
basedir = os.path.dirname(__file__)

#definisce la path di avatar: path corrente + path relativa
avatar_dir = os.path.join(basedir, "static/uploads/avatar")

#crea la cartella se non esiste e la crea e la mette nella cartella del file corrente
if not os.path.exists(avatar_dir):
    os.mkdir(avatar_dir)

db = MySQLdb.connect(
    host = app.config["HOST"], # your host, usually localhost
    user = app.config["USER"], # your username
    passwd = app.config["PASSWORD"], # your password
    db = app.config["DB"],
    use_unicode = True) # name of the data base

albums, photos = give_me_photos()


#main 
# mostra post
@app.route('/')
def show_entries():
    cur = db.cursor()
    
    cur.execute("""SELECT au.nome, path_su_disco, titolo, contenuto, DATE_FORMAT(DATE(data ),'%d %b %y') 
                FROM autori as au JOIN articoli as ar on au.id=ar.autore_id
                LEFT JOIN avatar as av on ar.avatar_id=av.id ORDER BY data DESC""")  
    entries = [dict(autor=row[0], avatar=row[1], title=row[2], text=row[3], date=row[4]) for row in cur.fetchall()]
    
    cur.execute("SELECT id, nome FROM autori ORDER BY nome ASC")     
    authors = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]
    
    cur.execute("SELECT id, path_su_disco FROM avatar ORDER BY id")     
    avatars = [dict(id=row[0], path=row[1]) for row in cur.fetchall()]
    
    return render_template('show_entries.html', entries=entries, authors=authors, avatars=avatars, fuoco="Home")

# aggiungi post
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    cur = db.cursor()
    cur.execute('INSERT INTO articoli (autore_id, avatar_id, titolo, contenuto, data) values (%s, %s, %s, %s, now())',
                 (request.form['autore'], request.form['avatar'], request.form['titolo'], request.form['contenuto']))
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

# fai il login
@app.route('/commander', methods=['GET', 'POST'])
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
    return render_template('foto.html', entries=entries, fuoco="Foto")
    
@app.route('/about')
def show_about():
    cur = db.cursor() 
   
    cur.execute("""SELECT au.nome, av.path_su_disco, au.descrizione
                FROM autori AS au LEFT JOIN avatar AS av ON au.avatar_id = av.id""")  
    abouts = [dict(autor=row[0], avatar=row[1], text=row[2]) for row in cur.fetchall()]
    
    print abouts
    return render_template('about.html', abouts=abouts, fuoco="About")

@app.route('/contatti')
def show_contatti():
    cur = db.cursor() 
    cur.execute("SELECT * FROM articoli")  
    entries = [dict(title=row[4], text=row[5]) for row in cur.fetchall()]
    return render_template('contatti.html', entries=entries, fuoco="Contatti")

#gestione errori
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="run the server with debug enabled",
                        action="store_true")
    args = parser.parse_args()
    if args.debug:
        print "verbosity turned on"
    
    app.debug = args.debug
    app.run(host='localhost')
