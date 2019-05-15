from flask import Flask, render_template, redirect, url_for, flash
from forms import bookmarkform, loginform, signupform
from flask import Flask, session
from flask_session import Session
from flask import url_for, redirect
import json
import os

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SESSION_TYPE'] = 'redis'

#Session trying
Session(app)
# Redis trying
REDIS_URL = "redis://localhost:6379/0"
from flask_redis import FlaskRedis
redis_store = FlaskRedis(app)

@app.route("/logout", methods=['GET','POST'])
@app.route("/login", methods=['GET','POST'])
def login():
    if (checklogin() == True):
        session['login'] = False
    login_form = loginform()
    if login_form.validate_on_submit():
        passphrase = returnsha256(login_form.passphrase.data)
        if passphrase.encode('utf-8') in redis_store.smembers("passphrase"):
            session['login']=True
            flash('Login successfull')
            return redirect(url_for('main'))
        else:
            flash('Invalid passphrase')
            return render_template('login.html', loginform= login_form)
    return render_template('login.html', loginform= login_form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    signup_form = signupform()
    if signup_form.validate_on_submit():
        existing_passphrase = signup_form.existing_passphrase.data
        new_passphrase = signup_form.new_passphrase.data
        hash_existing_pp = returnsha256(existing_passphrase)
        if( (hash_existing_pp.encode('utf-8')  in redis_store.smembers("passphrase")) and len(new_passphrase) >= 4 ):
            redis_store.sadd("passphrase", returnsha256(new_passphrase))
            flash('signup successfull')
            return render_template('login.html', loginform= loginform())
        else:
            flash('signup fail, existing passphrase invalid or new passphrase length < 4')
    return render_template('signup.html', signupform= signupform())


def checklogin():
    return True if(session.get('login') == True) else False

def returnsha256(value):
    import hashlib
    return hashlib.sha224((value+os.getenv("SALT")).encode("utf-8")).hexdigest()

@app.route("/index", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def main():
    if (checklogin()):
        users = redis_store.keys('user_*')
        name = [x.decode('UTF-8')[5:] for x in users]
        return render_template('main.html', author = name)
    else:
        return redirect(url_for('login'))


@app.route("/form", methods=['GET', 'POST'])
def form():
    if (checklogin()):
        bm_form = bookmarkform()
        if bm_form.validate_on_submit():
            link = bm_form.link.data
            #bm_form.description.data
            user = bm_form.author.data
            redis_store.sadd("user_"+user, link)
            redis_store.set(link, return_title(link))
            flash('successfully added!')
            return redirect(url_for('show_bookmark', word=user))
        users = redis_store.keys('user_*')
        name = [x.decode('UTF-8')[5:] for x in users]
        return render_template('form.html', bm_form = bm_form, author = name)
    else:
        return redirect(url_for('login'))

@app.route('/user/<word>')
def show_bookmark(word):
    # import pdb
    # pdb.set_trace()
    if (checklogin()):
        word = "user_"+ word
        if(redis_store.exists(str(word))):
            values = redis_store.smembers(str(word))
            list_ = [x.decode('UTF-8') for x in values ]
            title = list()
            for link in list_:
                try :
                    title.append((redis_store.get(link)).decode('UTF-8'))
                except:
                    title.append("Not Available")
            data = json.dumps([{'title':t1, 'link':link} for t1, link in zip(title, list_)])
            data = json.loads(data)
            return render_template('show_bookmark.html', data = data, author=word[5:])
        else:
            return "Key does not exists!"
    else:
        return redirect(url_for('login'))


def return_title(url_):
    import urllib.request as urllib2
    from bs4 import BeautifulSoup
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
        req = urllib2.Request(url_,headers=hdr)
        soup = BeautifulSoup(urllib2.urlopen(req),"html.parser")
        title = soup.title.string
    except:
        title = "Unable to fetch Title"
    return title

if __name__ == '__main__':
    app.run('127.0.0.1',port=8000)
