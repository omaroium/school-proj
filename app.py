from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
from datetime import datetime

tweet={}


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'


Config = {
  "apiKey": "AIzaSyBW232n5Lnogln0UNFG4cK6D-KScVGfexU",
  "authDomain": "finally-4dd8f.firebaseapp.com",
  "databaseURL": "https://finally-4dd8f-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "finally-4dd8f",
  "storageBucket": "finally-4dd8f.appspot.com",
  "messagingSenderId": "112476821739",
  "appId": "1:112476821739:web:9023ddd0cb5ff6c92746ae",
  "measurementId": "G-NYBE7M8ST7",
  "databaseURL":"https://finally-4dd8f-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase=pyrebase.initialize_app(Config)
auth = firebase.auth()
db=firebase.database()
#Initialize Firebase


@app.route('/signup', methods=['GET', 'POST'])
def signup():
   error = ""
   if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['username']
        firstname = request.form['firstname']

        login_session['user'] = auth.create_user_with_email_and_password(email, password)
        user = {"name": name, "email": email,"password":password,"firstname":firstname}
        db.child("Users").child(login_session['user']
        ['localId']).set(user)
        return redirect(url_for('signin'))
        error = "Authentication failed"
   return render_template("signup.html")

@app.route('/', methods=['GET', 'POST'])
def signin():

    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('add_tweet'))
        except:
            error = "Authentication failed"
    return render_template("signin.html")


@app.route('/add_tweet', methods=['GET', 'POST'])
def add_tweet():
    if request.method == 'POST':
       try:
           now = datetime.now()
           tweet={"title":request.form['title'],"text":request.form['text'], "uid": login_session['user']['localId'],"time":now.strftime("%d/%m/%Y %H"),"likes":0,"img":request.form['img'] }
           db.child("Tweets").push(tweet)
       except:
           print("Couldn't add article")
    return render_template("add_tweet.html",    tweets2=db.child("Tweets").get().val() ,current_user=login_session['user']['localId']
)

@app.route('/all_tweets', methods=['GET', 'POST'])
def all_tweet():
    if request.method == 'POST':
        print("YOOOOOOOOOOOOOOOOOO")
        try:
            print("yoyoyo")
            return render_template("tweets.html")
        except:
            print("Couldn't add article")
            redirect(url_for('add_tweet'))
    return render_template("tweets.html",tweets2=db.child("Tweets").get().val(),users=db.child("Users").get().val(), current_user=login_session['user']['localId'])

@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    login_session['user'] = None
    auth.current_user = None

@app.route('/like/<string:k>', methods=['GET', 'POST'])
def like(k):
    if request.method == 'POST':
        try:
            likes = {'likes' : db.child('Tweets').child(k).get().val()['likes'] + 1}
            db.child("Tweets").child(k).update(likes)
            return redirect(url_for('all_tweet'))
        except:
            return redirect(url_for('all_tweet'))
    return redirect(url_for('all_tweet'))


@app.route('/all_tweets/<string:user>', methods=['GET', 'POST'])
def page(user):
    utweets=[]

    tweet=db.child("Tweets").get().val()
    for x in tweet:
        if(tweet[x]['uid']==user):
           utweets.append(tweet[x])
    return render_template('user_page.html',tweets2=utweets, length=len(utweets),users=db.child("Users").get().val(),user=user,current_user=login_session['user']['localId'])




@app.route('/massage/<string:name>/<string:other>', methods=['GET', 'POST'])
def massage(name,other):
    utweets=[]
    tweet={"title":request.form['title'],"text":request.form['text'], "uido": other,"time":now.strftime("%d/%m/%Y %H"),"likes":0,"img":request.form['img'] }
    db.child('Massage').push(tweet)
    tweet=db.child("Massages").get().val()
    for x in tweet:
        if(tweet[x]['uid']==name and tweet[x]['uido']==other):
           utweets.append(tweet[x])

    return render_template("session.html",    users=db.child("Users").get().val(),len=len(utweets),tweets2=utweets ,current_user=login_session['user']['localId'],user=name,other=other
)
if __name__ == '__main__':
    app.run(debug=True)
