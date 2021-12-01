from flask import Flask, render_template, request, redirect, url_for,session, flash
from flaskext.mysql import MySQL
import pymysql
from pymysql import cursors


app = Flask(__name__)
app.secret_key='secret123'

#configure db

mysql = MySQL(app)

app.config['MYSQL_DATABASE_HOST'] = 'projectdb.cifjctjr38yf.us-east-1.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'tripad21'
app.config['MYSQL_DATABASE_DB'] = 'Project21'

#mysql.init_app(app)


@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

@app.route('/explore', methods=['GET','POST'])
def explore_page():

    if session.get('loggedin'):
        con = mysql.connect()
        cur = con.cursor()

        if request.method == 'GET':
            cur.execute("SELECT * FROM df_general2")
            itemsDetails = cur.fetchall() 

            user = session['userid']
            cur.execute("SELECT * from wishlist WHERE userid = %s", user)
            wishlistitems = cur.fetchall()


        if request.method == 'POST':
            itemAdd = request.form
            userid = itemAdd['userid']
            username = itemAdd['username']
            itemid = itemAdd['itemid']
            itemname = itemAdd['itemname']
            cur.execute("INSERT INTO wishlist(userid, username, itemid, itemname) VALUES (%s, %s, %s, %s)", (userid, username, itemid, itemname))
            con.commit()
            flash('Added successfully!','success')
            return redirect(url_for('explore_page'))

    else: 
        flash('Please log in to view the explore page!','danger')
        return redirect(url_for('login_page'))

    return render_template('explore.html', itemsDetails= itemsDetails, wishlistitems=wishlistitems)

@app.route('/review', methods=['GET','POST'])
def review_page():
    if session.get('loggedin'):
        con = mysql.connect()
        cur = con.cursor()
 
        cur.execute("SELECT * from df_reviews2 LIMIT 5000")
        itemReviews= cur.fetchall()
    
    else: 
        flash('Please log in to view the review page!','danger')
        return redirect(url_for('login_page'))
    return render_template('review.html', itemReviews= itemReviews)

@app.route('/register', methods=['GET','POST'])
def register_page():
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'pw' in request.form:
        #Fetch form data
        userDetails =  request.form
        username = userDetails['username']
        email = userDetails['email']
        pw = userDetails['pw']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute("INSERT INTO register(username, pw, email) VALUES (%s, %s, %s)", (username, pw, email))
        con.commit()
        cur.close()
        con.close()
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login_page():
    
    if request.method == 'POST' and 'username' in request.form and 'pw' in request.form:
        userDetails =  request.form
        username = userDetails['username']
        pw = userDetails['pw']

       
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * from register WHERE username=%s AND pw=%s", (username, pw))
        account= cur.fetchone()
        #cur.close()

        if account:
            session['loggedin'] = True
            session['userid'] = account['userid']
            session['username'] = account['username']
            flash('Logged in successfully','success')
            return redirect(url_for('explore_page'))
        else:
            flash('Invalid Login. Try Again','danger')
    return render_template('login.html')

@app.route("/logout")
def logout_page():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('home_page'))