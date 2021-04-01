import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
import re
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


def check_name(name):
    # Validates users names.
    # Allow lowercase and uppercase letters and numbers.
    return re.match("[a-zA-Z0-9]+$", name)


def check_password(password):
    # Validate users passwords.
    # Allow lowercase and uppercase letters and numbers,
    # 5-15 characters in length.
    return re.match("^[a-zA-Z0-9]{5,15}$", password)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/services")
def services():
    return render_template("services.html")


# Register Functionality
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":    
        # check if characters added for username are valid  
        if request.form.get("username") == "" or not check_name(
           request.form.get("username").lower()):
            flash("Username Invalid")
            return redirect(url_for("register"))
        
        # check if characters added for password are valid  
        if request.form.get("password") == "" or not check_password(
           request.form.get("password")):
            flash("Please enter a valid password.")
            return redirect(url_for("register"))
        
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # check if username already exists in db
        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if existing_email:
            flash("Email already exists")
            return redirect(url_for("register"))
        
        register = {
            "FirstName": request.form.get("FirstName"),
            "LastName": request.form.get("LastName"),
            "subscription": request.form.get("subscription"),
            "address": request.form.get("address"),
            "email": request.form.get("email"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})
    
    if session["user"]:    
        return render_template("profile.html", username=username)  
    
    return redirect(url_for("login"))


@app.route("/edit_profile/<username_id>", methods=["GET", "POST"])
def edit_profile(username_id):
        if request.method == "POST":
            existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

            if check_password_hash(
                existing_user["password"], request.form.get("password")):

                    update = {
                        "FirstName": request.form.get("FirstName"),
                        "LastName": request.form.get("LastName"),
                        "subscription": request.form.get("subscription"),
                        "address": request.form.get("address"),
                        "email": request.form.get("email"),
                        "username": request.form.get("username").lower(),
                        "password": generate_password_hash(request.form.get("password"))
                    }
                    mongo.db.users.update({"_id": ObjectId(username_id)}, update)
                    flash("Update Successful!")

            else:
                # invalid password match
                flash("Incorrect Password, Update not complete")

        user = mongo.db.users.find_one({"_id": ObjectId(username_id)})
        username = mongo.db.users.find_one({"username": session["user"]})
        return render_template("edit_profile.html", user=user, username=username)
    


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/book_class", methods=["GET", "POST"])
def book_class():
    if request.method == "POST":
        task = {
            "category_name": request.form.get("category_name"),
            "booking_name": request.form.get("booking_name"),
            "booking_date": request.form.get("booking_date"),
            "booking_time": request.form.get("booking_time"),
            "booking_notes": request.form.get("booking_notes"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Class Booked")
        return redirect(url_for("book_class"))
        
    categories = mongo.db.categories.find().sort("category_name", 1)
    tasks = mongo.db.tasks.find()
    return render_template("book_class.html", categories=categories, tasks=tasks)


@app.route("/edit_class/<task_id>", methods=["GET", "POST"])
def edit_class(task_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "booking_name": request.form.get("booking_name"),
            "booking_date": request.form.get("booking_date"),
            "booking_time": request.form.get("booking_time"),
            "booking_notes": request.form.get("booking_notes"),
            "created_by": session["user"]
        }
        mongo.db.tasks.update({"_id": ObjectId(task_id)}, submit)
        flash("Changes Saved")
        return redirect(url_for("book_class"))

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    tasks = mongo.db.tasks.find()
    return render_template("edit_class.html", task=task, categories=categories, tasks=tasks)


@app.route("/delete_class/<task_id>")
def delete_class(task_id):
    mongo.db.tasks.remove({"_id": ObjectId(task_id)})
    flash("Class Deleted")
    return redirect(url_for("book_class"))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)