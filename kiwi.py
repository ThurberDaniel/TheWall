from flask import Flask, render_template, redirect, request, session, flash
from connect5000 import connectToMySQL
import re
from flask_bcrypt import Bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ft67uhgf"

########## SHOWS MAIN PAGE #########################
@app.route("/")
def index():
    mysql = connectToMySQL('wall_sch')
    # friends = mysql.query_db('SELECT * FROM user_table;')
    return render_template("main.html")
################## END OF SHOW PAGE ################################

############## ADD USER _ INPUT VALIDATION ######################
@app.route("/add", methods=["POST", "GET"])
def input():
    is_valid = True
    if len(request.form['reg_fname']) < 2:
        flash("First Name should be at least 2 characters")
    if len(request.form['reg_lname']) < 2:
        flash("Last Name should be at least 2 characters")
    if len(request.form['reg_email']) < 5:
        flash("Please enter a valid email")
    if len(request.form['reg_pass']) < 5:
        flash("Password should be at least 5 characters")
    if request.form['reg_pass'] != request.form['con_pass']:
        flash("Password do not match- Please try again")

    if not EMAIL_REGEX.match(request.form['reg_email']):    
        flash("Invalid email address!")
    #-------CONNECTS AND CHECKS FOR EMAIL VALIDATION  ---------
    database = connectToMySQL('wall_sch')
    query = "SELECT * FROM user_table WHERE email= %(ema)s;"
    data = {
            'ema' : request.form['reg_email'],
        }
    result = database.query_db(query, data)
    if len(result)>0:  #IF A USER THAT ALREADY EXIST THEN FLASH MSG **** DO NOT ENTER ******
        flash("Email already in use - Please try again")
    if not '_flashes' in session.keys(): #IF THERE ARE NO FLASH MSG THEN PROCESS TO PUT INFO INTO DB
        flash("Successfully Added",)
        database = connectToMySQL('wall_sch')
        pw_hash = bcrypt.generate_password_hash(request.form['reg_pass'])
        print(pw_hash)
        query = "INSERT INTO user_table(first_name, last_name, email, password)VALUES(%(fn)s,%(ln)s,%(em)s,%(pass)s);"
        qwerty = {
                'fn' : request.form['reg_fname'],
                'ln' : request.form['reg_lname'],
                'em' : request.form['reg_email'],
                'pass': pw_hash,
        }
        info=database.query_db(query,qwerty)
        queryDB = "SELECT * FROM user_table WHERE email = %(eml)s;" #ROADMAP INTO THE EMAIL IN THE DB

        dataDB = {
            "eml" : request.form['reg_email'],
        }
        db = connectToMySQL('wall_sch') # linking db 
        show = db.query_db(queryDB,dataDB)
        session['userid'] = show[0]['id_track']
        session['fn'] = show[0]['first_name']


        return redirect("/wall/message")
    else:
        return redirect("/")
################# END OF ADD USER W/ VALIDATION #########################

####################### MESSAGE ###############################
@app.route("/wall/message")
def msg():
    mysql = connectToMySQL("wall_sch")
    qwerty = "SELECT id_track, first_name  FROM user_table WHERE id_track <> %(id)s;"
    data={
        "id" : session['userid']
    }
    result = mysql.query_db(qwerty,data)
    ##----   -  - - - - -- - -- - - - -- - - - 
    mysql = connectToMySQL("wall_sch")
    qwerty3="SELECT user_table.first_name, message_table.message, message_table.id_track FROM user_table JOIN message_table ON sender_id = user_table.id_track WHERE message_table.reciever_id =%(id)s;"
    data3={
        "id" : session['userid'],
    }
    result2 = mysql.query_db(qwerty3,data3)

##----GET SESSION USER FIRST NAME TO BE DISPLAYED -------------
    mysql = connectToMySQL("wall_sch")
    qwerty2 ="SELECT first_name FROM user_table WHERE id_track = %(fn)s;"
    data2={
        "fn": session['userid']
    }
    resultz = mysql.query_db(qwerty2,data2)
    #-------------------------
    mysql = connectToMySQL("wall_sch")
    query='SELECT COUNT(messages.recipient_id) FROM messages WHERE messages.recipient_id=users_users_id;'


    return render_template("show.html", show=resultz, showing=result, appearing= result2)
#################### END OF MESSAGE ###########################



##############  PROCESS  ###################################
@app.route("/process/<id>", methods=["POST"])
def help_me_code_gods(id):
    mysql = connectToMySQL("wall_sch")
    qwerty = "INSERT INTO message_table(message,sender_id,reciever_id) VALUES (%(msg)s,%(snd)s,%(rcr)s); "
    data = {
        "msg" : request.form['text'],
        "snd" : session['userid'],
        "rcr" : id,
    }
    resultz = mysql.query_db(qwerty,data)
    return redirect("/wall/message")
############### END OF PROCESS #######################

####### DELETE MSG ##############################
@app.route('/delete/<id>')
def delete(id):
    mysql = connectToMySQL("wall_sch")
    deleter= "DELETE FROM message_table WHERE message_table.id_track = %(id)s"
    info = {
        'id': id
    }
    print("*********************@")
    print(deleter)
    print(info)
    print("*********************@")
    stuff = mysql.query_db(deleter, info)
    return redirect('/wall/message')
#### END OF DELETE #########################



######### HTML SHOW PAGE WITH DB INFORMATION #################
@app.route("/wall", methods=["GET"] )
def so1o():
    if  not "userid" in session:
        return redirect("/logout")
    return render_template('show.html')
########## END OF SHOW PAGE #######################



#########  LOG IN ###############################
@app.route('/WelcomeBack', methods=['POST'])
def login():   # see if the username provided exists in the database
    mysql = connectToMySQL("wall_sch")
    query = "SELECT * FROM user_table WHERE email = %(ema)s;"
    data = {
        "ema" : request.form["log_email"],
        }
    result = mysql.query_db(query, data)

    if len(result) > 0:
        if not request.form["log_pass"] =="":
            pw_hash = bcrypt.generate_password_hash(request.form['log_pass'])
            print (pw_hash)
            if bcrypt.check_password_hash(result[0]['password'], request.form['log_pass']):
                # if we get True after checking the password, we may put the user id in session
                session['userid'] = result[0]['id_track']
                # never render on a post, always redirect!
                return redirect('/wall/message')
    flash("You could not be logged in - Try Again!")
    return redirect("/")
################# END OF LOG-IN  ##########################




# LOGOUT USER /// CLEAR SESSION #############################
@app.route('/logout',methods=['GET'])
def logout(): 
    session.clear()
    flash("You have been logged out - Please return soon!")
    return redirect('/')
###################### END OF LOG OUT #####################

if __name__ == "__main__":
    app.run(debug=True)





