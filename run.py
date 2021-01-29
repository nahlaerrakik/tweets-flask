__author__ = 'nahla.errakik'

import os
from flask import Flask, render_template, request, redirect
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Search, db, login
from pyTwitter import Twitter

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'xyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)


@app.before_first_request
def create_all():
    db.create_all()


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        print("ICH BIN IN LOGIN")
        return redirect('/searchafterlogin')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User().get_user(email)

        if user is None:
            return render_template('login.html', error_msg='User not found')
        elif not user.check_password(password):
            return render_template('login.html', error_msg='Password is not correct')
        else:
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user = User().get_user(email)

        if user:
            render_template('register.html', error_msg='User already exist !')
        else:
            username = request.form['username']
            password = request.form['password']
            User().add_user(username, password, email)

            return render_template('login.html')

    return render_template('register.html')


@app.route('/searchafterlogin')
@login_required
def tweets_login():
    return render_template('tweets_login.html')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    tweets = Search().search(keyword)

    if len(tweets) > 0:
        if Search.less_than_5minutes(tweets[0].creation_time):
            # tweets = []
            # for x in tweets:
            #     dictionar = {'text': x.text}
            #     tweets.append(dictionar)
            tweets = [{'text': x.text} for x in tweets]
        else:
            print("insert new tweets in db")
            search_result = Twitter().search_tweets(keyword)
            tweets = search_result['statuses']
            for item in tweets:
                tweet = Search(keyword=keyword, text=item['text'])
                Search().add_search(tweet)
    # Keyword isn t in DB
    else:
        print("!!!!!!!!!!!NOT FOUND IN DATABASE")
        search_result = Twitter().search_tweets(keyword)
        tweets = search_result['statuses']
        for item in tweets:
            tweet = Search(keyword=keyword, text=item['text'])
            Search().add_search(tweet)

    return render_template("index.html", tweets=tweets, keyword=keyword)


@app.route('/store', methods=['GET', 'POST'])
def store():
    keyword = request.form['keyword']

    ar = 0
    return
    """# userId = session.query(User).get(1)
    # user = UserModel.query.filter_by(id=userId).first()
    # conn.execute('SELECT id FROM author_table').fetchall()
    if request.method == 'POST':
        keyword = request.form['add']
        print(keyword)
        row = get_tweets_from_db2(keyword)
        print(row)
        search_result = Twitter().search_tweets(keyword)
        tweets = search_result['statuses']
        insert_tweets_user(keyword, tweets)
        return redirect(url_for('home'))

    else:
        return render_template('login.html')
    # with sqlite3.connect(os.path.join(DIR_NAME, DB)) as conn:
    # conn.execute('CREATE TABLE IF NOT EXISTS UserTweets (keyword TEXT, text TEXT)')"""


if __name__ == "__main__":
    app.run(debug=True)
