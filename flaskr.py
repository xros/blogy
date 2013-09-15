# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect,url_for, abort, render_template, flash

# this module is used to auto-closing context session when \
# sql database operation is finished
# it has the same function of " xxx.close() "
#######################################
# con = sqlite3.connect('census.db')
# cur = con.cursor()
# cur.execute('CREATE TABLE Density(Region TEXT, Population INTEGER, Area REAL)')
# [and lots of SQL operation]
# cur.close()
# con.close()
#######################################
# Please visit http://www.cnblogs.com/spaceship9/archive/2013/04/25/3042870.html
#######################################
from contextlib import closing


# configuration
DATABASE = '/home/phone/sandbox/env_27_flask/blogy/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app= Flask(__name__)

# [ Flask basic settings ]
# from_object() will look at the given object ( if it's a string it will \
# import it) and then look for all uppercase variables defined there. In our \
# case, the configuration we just wrote a few lines of code above. You can \
# also move that into a separate file
# [Note:] Flask has two ways to import configuration files
#               1. app.config.from_object(__name__)
#               2. app.config.from_envvar('FLASKR_SETTINGS', silent=True)
# [In this case] we choose way 1.
# Here we see

app.config.from_object(__name__)



# This will create a environmental variable called FLASKR_SETTINGS to specify \
# a config file to be loaded wich will then override the default values. \
# The silent switch just tells Flask to not complain if no such environment key\
# is set.
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# The secret_key is needed to keep the client-side sessions secure.
# Choose the key wisely and as hard to guess and complex as possible


# [ prepare for database]
# *connect db*
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])      
# [in this case] app.config['DATABASE'] ==> DATABASE = '/tmp/flaskr.db'


# *initialize db*
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# [organical solution: request with database for opening and closing ]
# organically open database session before request
@app.before_request
def before_request():
    g.db = connect_db()

# organically close database session after request
@app.teardown_request
def teardown_request(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()



# [the view functions]
# *show entries*
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    # you gonna love dict to the utmost :)
    entries = [ dict(title = row[0], text = row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries = entries)


# *add new entry*
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?,?)',[request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was sucessfully posted')
    return redirect(url_for('show_entries'))    # redirect the URL where is hooked up with 
                                                # function 'show_entries'

# [security note]
# Login and logout
# *login*
@app.route('/login', methods = ['GET', 'POST'])
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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error = error)


# *logout*
@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))



if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
