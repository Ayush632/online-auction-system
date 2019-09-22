import os

from flask import Flask
from flask_socketio import SocketIO, emit

from flask import jsonify, render_template, request
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlite3
import mysql.connector

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

@app.route('/')
def login():
    return render_template('login.html')
@app.route("/check",methods=["POST"])
def check():
 
 # cur=conn.cursor()
  name=request.form.get("user_name")
  #print(type(name))
  passw=request.form.get("password")
  conn = None
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '9290827021')
  #if conn.is_connected():
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
  
@app.route("/sign_up")
def sign():
    return render_template('sign.html')
@app.route("/one",methods=["GET","POST"])
def first():
  #  conne=sqlite3.connect('auction.sqlite')
  #  cure=conne.cursor()
    name=request.form.get("user_name")
    passw=request.form.get("password")
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    email_id=request.form.get("email_id")
    ph_no=request.form.get("ph_no")
    conn = None
    conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '9290827021')
    cursor=conn.cursor()
    cursor.execute("use prj")
    cursor.execute("select * from user")
    row=cursor.fetchall()
    flag=0
    for r in row:
      if(r[0] is name):
        flag=1
        break
      if(r[4] is email_id):
        flag=1
        break
      if(r[5] is ph_no):
        flag=1
        break
    if flag is 1:
      conn.close()
      return render_template("login.html")
    else:
      cursor.execute("""insert into user values (%s,%s,%s,%s,%s,%s)""",(name,passw,first_name,last_name,email_id,ph_no))
      conn.commit()
      conn.close()
      return render_template("options.html")
  
