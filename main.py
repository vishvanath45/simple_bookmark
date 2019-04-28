from flask import Flask, render_template, redirect, url_for
from forms import bookmarkform
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f21f2b617a'

# Redis trying
REDIS_URL = "redis://localhost:6379/0"
from flask_redis import FlaskRedis
redis_store = FlaskRedis(app)

@app.route("/", methods=['GET', 'POST'])
def main():
    users = redis_store.keys('user_*')
    name = [x.decode('UTF-8')[5:] for x in users]
    return render_template('main.html', author = name)

@app.route("/form", methods=['GET', 'POST'])
def form():
    bm_form = bookmarkform()
    if bm_form.validate_on_submit():
        link = bm_form.link.data
        #bm_form.description.data
        user = bm_form.author.data
        redis_store.sadd("user_"+user, link)
        redis_store.set(link, return_title(link))
        return redirect(url_for('show_bookmark', word=user))
    return render_template('form.html', bm_form = bm_form)

@app.route('/user/<word>')
def show_bookmark(word):
    #print(word, type(word))
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
        # print(data)
        data = json.loads(data)
        return render_template('show_bookmark.html', data = data, author=word[5:])
    else:
        return "Key does not exists!"



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
        soup = BeautifulSoup(urllib2.urlopen(req))
        title = soup.title.string
    except:
        title = "Unable to fetch Title"
    return title

if __name__ == '__main__':
    app.run()
