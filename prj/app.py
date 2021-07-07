from flask import Flask
from flask_socketio import SocketIO, emit
from flask import jsonify, render_template, request
import mysql.connector

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route("/check",methods=["POST"])
def check():
    name=request.form.get("user_name")
    passw=request.form.get("password")
    conn = None
    conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '9290827021')
  
    cursor=conn.cursor()
    cursor.execute("use prj")
    cursor.execute("select * from user")
    row=cursor.fetchall()
    for i in row:
        if (i[0]==name):
            if(i[1]==passw):
                print("verified")
                conn.close()
                return render_template('options.html')
    print("not verified")
    conn.close()
    return render_template('login.html')