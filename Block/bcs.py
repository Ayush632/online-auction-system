from flask import Flask,render_template,request,make_response,send_from_directory
import mysql.connector
from mysql.connector import Error
import threading
import datetime
import os
import json
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO,emit

# # set FLASK_APP=main.py
# # python -m flask run

# UPLOAD_FOLDER = """C:\DBMS Project\static"""
# ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)




# @app.route('/home_pg')
# def home_pg():
#     return render_template('homepage.html')

@app.route('/a',methods=['GET','POST'])
def home_pg():
    ss=str(request.form['q'])
    return json.loads('{"a":"file"}')


if __name__ == "__main__":
    # socketio.run(app)
    app.run(host='0.0.0.0',port=5001)