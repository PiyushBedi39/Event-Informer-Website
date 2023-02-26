from flask import Flask, render_template, request, url_for, redirect, session, flash
import pymongo
import bcrypt

app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://admin:adminpassword@cluster0.bqoatrf.mongodb.net/?retryWrites=true&w=majority")

db = client.get_database("registration_records")
records = db.register


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/event")
def event():
    if "email" not in session:
        flash("Please log in to see events", category="error")
        return redirect(url_for('login'))
    return render_template('event.html')

@app.route("/login/",methods = ['POST','GET'])
def login():

    print(session)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check email exists in records(db)
        email_found = records.find_one({'email':email})
        if email_found:
            email_val =email_found["email"]
            passcheck = email_found["password"]
            #check password
            if bcrypt.checkpw(password.encode("utf-8"),passcheck):
                session["email"] = email_val
                name = records.find_one({"email":email_val}).get("name")
                session["name"] = name
                print(session)
                
                return redirect(url_for('event'))
            else:
                flash("Incorrect Password", category="error")
                return render_template('login.html')
        else:
            flash("Email account does not exist", category="error")
            return render_template('login.html')

    return render_template('login.html')


@app.route("/signup",methods = ['POST','GET'])
def signup():
    if 'email' in session:
        return render_template('base.html')
    
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        contact_no = request.form.get("contactno")
        #we will use this when required
        # home_address = request.form.get("homeaddress")
        # profession = request.form.get("profession")
        # socialmedia = request.form.get("socialmediahandle")
        password1 = request.form.get("Password1")
        password2 = request.form.get("Password2")

        user_found = records.find_one({"name":user})
        email_found = records.find_one({"email":email})
        if user_found:
            flash("User already exists",category="error")
            # return render_template('signup.html')
        elif email_found:
            flash("Email already registered",category="error")
            # return render_template('signup.html')
        elif len(contact_no) != 10:
            flash("Invalid Phone Number",category="error")
        elif len(password1) < 7:
            flash("Password length should be more than 7", category="error")
        elif password1 != password2:
            flash('Password does not match',category="error")
            # return render_template('signup.html')
        else:
            #hash password
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name':user,
                          'email':email,
                          'contact_no':contact_no,
                          'password':hashed}
            #insert in db
            records.insert_one(user_input)

            
            flash('Account Created',category="success")
            
            return redirect(url_for('login'))
        
    return render_template('signup.html')
@app.route('/logout')
def logout():
    if "email" in session:
        session.pop("email",None)
        session.pop("name",None)
        return redirect(url_for('login'))
    else:
        return render_template("index.html")


if __name__=="__main__":
    app.run(debug=True)