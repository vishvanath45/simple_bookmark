from flask import Flask, render_template, redirect, url_for
from forms import bookmarkform

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f21f2b617a'

# Redis trying
REDIS_URL = "redis://localhost:6379/0"
from flask_redis import FlaskRedis
redis_store = FlaskRedis(app)

@app.route("/", methods=['GET', 'POST'])
def main():
    users = redis_store.keys('*')
    name = [x.decode('UTF-8') for x in users]
    return render_template('main.html', author = name)

@app.route("/form", methods=['GET', 'POST'])
def form():
    bm_form = bookmarkform()
    if bm_form.validate_on_submit():
        link = bm_form.link.data
        #bm_form.description.data
        user = bm_form.author.data
        #print(link, user)
        redis_store.sadd(user, link)
        return redirect(url_for('show_bookmark', word=user))
    return render_template('form.html', bm_form = bm_form)

@app.route('/user/<word>')
def show_bookmark(word):
    #print(word, type(word))
    if(redis_store.exists(str(word))):
        values = redis_store.smembers(str(word))
        list_ = [x.decode('UTF-8') for x in values ]
        return render_template('show_bookmark.html', list1=list_, author=word)
    else:
        return "Key does not exists!"

if __name__ == '__main__':
    app.run()
