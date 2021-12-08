from flask import Flask, render_template, request, redirect, url_for,session, flash
from flaskext.mysql import MySQL
import pymysql
from pymysql import cursors

import numpy as np
import random
import tensorflow as tf

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
            cur.execute("SELECT * from wishlist1 WHERE userid = %s", user)
            wishlistitems = cur.fetchall()


            def rec_model(user1):
                if user1 > 21869:
                    user = random.sample(range(1,21869,1),1)[0]
                else:
                    user = user1
                
                cur.execute("select user_loc from df_reviews2 where user_id =  %s", user)
                user_loc = cur.fetchone()[0]
                model_re=tf.saved_model.load("re_testing1")
                model_rank=tf.saved_model.load("rank_testing")

                reviewed_items = []
                U_reviews = cur.execute("select title from df_reviews2 where user_id =  %s", user1)
                for i in cur.fetchall():
                   reviewed_items.append(i[0])
                U_wishitems = cur.execute("select itemname from wishlist1 where userid =  %s", user1)
                for i in cur.fetchall():
                    reviewed_items.append(i[0])


                scores, titles = model_re({"user_id":np.array([str(user)]), "user_loc":np.array([str(user_loc)])})
                retrieval_result = [i.decode('utf-8') for i in titles.numpy()[0]]
                rank_items = [item for item in retrieval_result if item not in reviewed_items][0:300]
                rank_ratings = {}
                for item_title in rank_items[0:20]:
                    rank_ratings[item_title] = model_rank({"user_id": np.array([str(user)]),"title": np.array([item_title])})
                Top_rec = []  
                for title, score in sorted(rank_ratings.items(), key=lambda x: x[1], reverse=True):
                    Top_rec.append(title)
                rec_items = Top_rec[0:10]
                
                cur.execute(f"select title from df_general2 where category_desc = (select category_desc from df_general2 as a left join wishlist1 as b on a.title = b.itemname where userid = {user1} order by datetime desc limit 1)")
                sub_cat_list = [i[0] for i in cur.fetchall()]
                same_cat_items = [item for item in rank_items if item in sub_cat_list and item not in rec_items] 
                rec_items = rec_items[0:10] + same_cat_items[0:4]
                rec_items = random.sample(rec_items,10)
                return rec_items
            
            rec_items = rec_model(session['userid'])


        if request.method == 'POST':
            itemAdd = request.form
            userid = itemAdd['userid']
            username = itemAdd['username']
            itemid = itemAdd['itemid']
            itemname = itemAdd['itemname']
            cur.execute("INSERT INTO wishlist1(userid, user_name, itemid, itemname) VALUES (%s, %s, %s, %s)", (userid, username, itemid, itemname))
            con.commit()
            flash('Added successfully!','success')
            return redirect(url_for('explore_page'))

    else: 
        flash('Please log in to view the explore page!','danger')
        return redirect(url_for('login_page'))

    return render_template('explore.html', itemsDetails= itemsDetails, wishlistitems=wishlistitems, rec_items=rec_items)

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