from flask import redirect, render_template,request
from main import app
from application.database import db
from application.models import *
import requests
from datetime import datetime

#Landing page
@app.route("/")
def home():
    return render_template("landing.html")

#Operations on user
#Login page
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    #if new user, go to signup (/signup)
    if request.method == 'POST':
        #check if user is there
        u = Users.query.filter_by(username=request.form["username"]).first()
        #if no
        if u is None:
            #flash error message
            return render_template("login.html",flag=1)
        return redirect("/%s/dashboard"%u.user_id)

#Signup page
@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == "POST":
        u = Users.query.filter_by(username=request.form["username"]).first()
        #if username is already there
        if u:
            #flash error message
            return render_template("signup.html",flag=2)
        else:
            data = Users(username = request.form["username"], name = request.form["name"])
            db.session.add(data)
            db.session.commit()
            #flash successful registration message
            return render_template("signup.html",flag=1)

#Dashboard
@app.route("/<int:user_id>/dashboard")
def get_trackers(user_id):
    #Querying Trackers table, to see if there is any tracker made by the user.
    ut = Trackers.query.filter_by(created_by= user_id).all()
    #Querying Users table, just to get the name of user, to display on dashboard.
    u = Users.query.filter_by(user_id=user_id).first()
    if u is None:
        return ('User does not exists')
    #So, if there are no trackers made by the user, then render appropriate template
    if len(ut) == 0:
        return render_template("dashboard.html",flag =0,u=u,ut=ut,user_id=user_id)
    #else, render appropriate template
    else:
        return render_template("dashboard.html",flag=1,u=u,ut = ut,user_id=user_id)


#CRUD on tracker

#Create
@app.route("/<int:user_id>/dashboard/create_tracker", methods=["GET","POST"])
def create(user_id):
    #Querying Users table, just to get the name of user, to display on dashboard.
    u = Users.query.filter_by(user_id=user_id).first()
    if request.method == 'GET': 
        return render_template("createtracker.html",user_id=user_id,u=u)
    if request.method == 'POST':
        data = {
                "name":request.form["name"],
                "description":request.form["description"],"tracker_type":request.form["tracker_type"], "settings":request.form["settings"]
                }
        api_url = "http://127.0.0.1:5000/api/trackers/"+str(user_id)
        r = requests.post(api_url,data=data)
        if r.status_code == 409:
            return render_template("createtracker.html",user_id=user_id,u=u,flag=0)
        return redirect("/%s/dashboard"%user_id)

#Read
@app.route("/<int:user_id>/dashboard/<int:tracker_id>")
def tracker_details(user_id,tracker_id):
    api_url = "http://127.0.0.1:5000/api/trackers/"+str(user_id)+"/"+str(tracker_id)
    ut = Trackers.query.filter_by(tracker_id=tracker_id, created_by=user_id).first()
    u = Users.query.filter_by(user_id=user_id).first()
    r = requests.get(api_url)
    if r.status_code == 404:
        return render_template("trackerpage.html",ut=ut,u=u,user_id=user_id,tracker_id=tracker_id,flag=0)
    resp = r.json()
    return render_template("trackerpage.html", data = resp, ut=ut,u=u,user_id=user_id,tracker_id=tracker_id,flag=1,l=resp)

#Update
@app.route("/<int:user_id>/dashboard/<int:tracker_id>/update", methods=["GET","POST"])
def updatetracker(user_id,tracker_id):
    u = Users.query.filter_by(user_id=user_id).first()
    t = Trackers.query.filter_by(tracker_id=tracker_id, created_by=user_id).first()
    if request.method == "GET":
        return render_template("edittracker.html",user_id=user_id,tracker_id=tracker_id,u=u,t=t)
    if request.method == "POST":
        data = {"name":request.form["name"],"description":request.form["description"]}
        api_url = "http://127.0.0.1:5000/api/trackers/"+str(user_id)+"/"+str(tracker_id)
        r = requests.put(api_url,data=data)
        if r.status_code == 409:
            return render_template("edittracker.html",user_id=user_id,tracker_id=tracker_id,u=u,t=t,flag=1)
        return redirect("/%s/dashboard"%user_id)

#Delete
@app.route("/<int:user_id>/dashboard/<int:tracker_id>/delete")
def deletetracker(user_id,tracker_id):
    api_url = "http://127.0.0.1:5000/api/trackers/"+str(user_id)+"/"+str(tracker_id)
    r= requests.delete(api_url)
    return redirect("/%s/dashboard"%user_id)

#CRUD on Logs

#Create
@app.route("/<int:user_id>/dashboard/<int:tracker_id>/add_log", methods=["GET","POST"])

def add_log(user_id,tracker_id):
    if request.method =="GET":
        dt = datetime.now()
        u = Users.query.filter_by(user_id=user_id).first()
        ut = Trackers.query.filter_by(tracker_id=tracker_id).first()
        if ut.tracker_type == 'Multiple Choice':
            l = []
            for i in ut.settings.split(","):
                l.append(i.strip())
            return render_template("newlog.html",user_id=user_id,tracker_id=tracker_id,ut=ut,u=u,dt=dt,flag=2,l=l)
        if ut.tracker_type == 'Boolean':
            return render_template("newlog.html",user_id=user_id,tracker_id=tracker_id,ut=ut,u=u,dt=dt,flag=3)
            
        return render_template("newlog.html",user_id=user_id,tracker_id=tracker_id,ut=ut,u=u,dt=dt,flag=1)

    if request.method == 'POST':
        data = {"timestamp":request.form["timestamp"], "value":request.form["value"], "note":request.form["note"]}
        api_url = "http://127.0.0.1:5000/api/trackerlogs/"+str(user_id)+"/"+str(tracker_id)
        r = requests.post(api_url,data=data)
        if r.status_code==201:
            return redirect("/%s/dashboard/%s"%(user_id,tracker_id))

#Update
@app.route("/<int:user_id>/dashboard/<int:tracker_id>/<int:log_id>/update",methods = ["GET","POST"])

def updatelog(user_id,tracker_id,log_id):
    if request.method=="GET":

        u = Users.query.filter_by(user_id=user_id).first()
        ut = Trackers.query.filter_by(tracker_id=tracker_id).first()
        log = Logs.query.filter_by(log_id=log_id).first()
        if ut.tracker_type == 'Multiple Choice':
            l = []
            for i in ut.settings.split(","):
                l.append(i.strip())
            return render_template("updatelog.html",user_id=user_id,tracker_id=tracker_id,ut=ut,u=u,flag=2,l=l,log=log,log_id=log_id)
        if ut.tracker_type == 'Boolean':
            return render_template("updatelog.html",user_id=user_id,tracker_id=tracker_id,ut=ut,u=u,flag=3,log=log,log_id=log_id)
            
        return render_template("updatelog.html",user_id=user_id,tracker_id=tracker_id,ut=ut,u=u,flag=1,log=log,log_id=log_id)

    if request.method == "POST":
        data = {"timestamp":request.form["timestamp"], "value":request.form["value"], "note":request.form["note"]}
        api_url = "http://127.0.0.1:5000/api/trackerlogs/"+str(user_id)+"/"+str(tracker_id)+"/"+str(log_id)
        r = requests.put(api_url,data=data)
        if r.status_code==200:
            return redirect("/%s/dashboard/%s"%(user_id,tracker_id))


#Delete
@app.route("/<int:user_id>/dashboard/<int:tracker_id>/<int:log_id>/delete")
def delete_log(user_id,tracker_id,log_id):
    api_url = "http://127.0.0.1:5000/"+"api/trackerlogs/"+str(user_id)+"/"+str(tracker_id)+"/"+str(log_id)
    r = requests.delete(api_url)
    if r.status_code == 200:
        return redirect("/%s/dashboard/%s"%(user_id,tracker_id))


