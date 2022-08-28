from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
from datetime import datetime

tweet={}


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'


Config = {
  "apiKey": "AIzaSyB8mcn93dHFC0JumKFYDdvlEr_R_ZMIQE8",
  "authDomain": "school-finalproj.firebaseapp.com",
  "databaseURL": "https://school-finalproj-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "school-finalproj",
  "storageBucket": "school-finalproj.appspot.com",
  "messagingSenderId": "157803470609",
  "appId": "1:157803470609:web:71301de1b5d0c9d0e5f6b0",
  "measurementId": "G-BWZ6326WFZ",
  "databaseURL":"https://school-finalproj-default-rtdb.europe-west1.firebasedatabase.app/"
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
    post=list(reversed(sorted(db.child("Tweets").get().val().keys())))
    if request.method == 'POST':
        print("YOOOOOOOOOOOOOOOOOO")
        try:
            print("yoyoyo")
            return render_template("tweets.html")
        except:
            print("Couldn't add article")
            redirect(url_for('add_tweet'))
    return render_template("tweets.html",tweets2=db.child("Tweets").child().get().val(),users=db.child("Users").get().val(), current_user=login_session['user']['localId'],postl=post)

@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    login_session['user'] = None
    auth.current_user = None

@app.route('/like/<string:k>', methods=['GET', 'POST'])
def like(k):
    if request.method == 'POST':
            likes = {'likes' : db.child('Tweets').child(k).get().val()['likes'] + 1}
            db.child("Tweets").child(k).update(likes)
            return redirect(url_for('all_tweet'))

    return redirect(url_for('all_tweet'))


@app.route('/all_tweets/<string:user>', methods=['GET', 'POST'])
def page(user):
    utweets=[]
    utweetsid=[]
    hi=user
    tweet=db.child("Tweets").get().val()
    for x in db.child("Tweets").get().val():
        if(tweet[x]['uid']==user):
           utweetsid.append(x)
           utweets.append(db.child("Tweets").get().val()[x])
    utweets.reverse()
    utweetsid.reverse()
    if request.method == 'POST':
        mlist=["hi"]
        current_user=login_session['user']['localId']
        isThere=False

        session={'uid':current_user,'uido':user,'massages':mlist}
        usersk=db.child("Masseges").child().get().val()

        for x in usersk:
            if (user == usersk[x]['uido'] and current_user == usersk[x]['uid']) or (current_user == usersk[x]['uido'] and user == usersk[x]['uid']):
                isThere=True
                print(usersk[x])
                print(isThere)
                if isThere:
                    return redirect(url_for('massage1',other=x))
        if not (isThere):
            db.child("Masseges").push(session)


    return render_template('user_page.html',posts=tweet,utweetsid=utweetsid,tweets2=utweets, length=len(utweets),users=db.child("Users").child().get().val(),user=hi,current_user=login_session['user']['localId'], usersk=db.child("Masseges").child().get().val())


@app.route('/sendmassage/<string:other>', methods=['GET', 'POST'])
def massage1(other):
    now = datetime.now()
    if request.method == 'POST':
           massage={"title":request.form['title'],"text":request.form['text'], "uid": login_session['user']['localId'],"uido":other,"time":now.strftime("%d/%m/%Y %H"),"likes":0,"img":request.form['img'] }
           mlist=db.child("Masseges").child(other).child('massages').get().val()
           mlist.append(massage)
           print(mlist)
           db.child("Masseges").child(other).update({'massages':mlist})
           return redirect(url_for('massage',name=other))

    return render_template("masseges.html",   massages=db.child("Masseges").get().val() ,current_user=login_session['user']['localId'] ,user=other ,session=db.child("Users").child().get().val(),thing=db.child("Masseges").child().get().val()
)


@app.route('/massage/<string:name>', methods=['GET', 'POST'])
def massage(name):
    masseges=db.child("Masseges").child(name).child('massages').get().val()


    return render_template("session.html",masseges=masseges,users=db.child("Users").child().get().val())




@app.route('/delete/<string:k>', methods=['GET', 'POST'])
def delp(k):
    if request.method == 'POST':
            db.child("Tweets").child(k).remove()

    return redirect(url_for('all_tweet'))

if __name__ == '__main__':
    app.run(debug=True)
