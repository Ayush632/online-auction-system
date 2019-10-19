import os
import json
from flask import Flask
from flask_socketio import SocketIO, send
from datetime import datetime
from flask import jsonify, render_template, request
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlite3
import smtplib
import mysql.connector
from pymongo import MongoClient
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
name=None
pid=2
@app.route('/')
def login():
    return render_template('login.html')


   
@app.route("/check",methods=["POST","GET"])
def check():
 
 # cur=conn.cursor()
  global name
  name=request.form.get("user_name")
  #print(type(name))
  
  passw=request.form.get("password")
  conn = None
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
  #if conn.is_connected():
  cursor=conn.cursor()
  cursor.execute("use prj2")
  cursor.execute("select * from user")
  row=cursor.fetchall()
  if request.method == "GET":
    prodid=(int)(request.args.get("prodid"))
    addnotify(prodid)
    conn.commit()
    cursor.execute("""select * from product
    left join 
    (select avg(points),reci from rating group by reci) as p
    on product.username=p.reci
    where not exists(select * from purchase
    where product.id=purchase.productid)
    """)
    products=cursor.fetchall()
    l=len(products)
    print(products)
    conn.close()
    return render_template("options.html",products=products,l=l)
  for i in row:
    if (i[0]==name):
      if(i[1]==passw):
          print("verified")
          conn.commit()
          cursor.execute("""select * from product
left join 
(select avg(points),reci from rating group by reci) as p
on product.username=p.reci
where not exists(select * from purchase
					where product.id=purchase.productid)
""")
          products=cursor.fetchall()
          l=len(products)
          print(products)
          conn.close()

          return render_template("options.html",products=products,l=l)
          #return render_template('options.html')
  print("not verified")
  conn.close()
  return render_template('login.html')
def icheck():
   conn = None
   conn = mysql.connector.connect(host='localhost',user='ayush',password= '')
   cursor=conn.cursor(buffered=True)
   cursor.execute("use prj2")
   cursor.execute("""select * from bid ORDER BY btime ASC""" )
   last=cursor.fetchone()
   dateTimeObj = datetime.now()
   difference = dateTimeObj - last[0]
   if (difference.seconds/60)>156738:
     cursor.execute("""update purchase set amount =%s , ptime =current_timestamp(), username=%s""",(last[1],last[2]))
     conn.commit()
     cursor.execute("""select *from product where not exists(select * from purchase where purchase.productid=product.id) order by id asc""" )
     newp=cursor.fetchone()
     cursor.execute("""insert into purchase values(%s,current_timestamp(),%s,NULL)""",(newp[3],newp[0]))
     conn.commit()
     client = MongoClient("127.0.0.1:27017")
     mydb=client['prj']
     mycol=mydb["notific"]
     mydoc=mycol.find({"prodid":newp[0]})
     for q in mydoc:
       sendm(q["mail"][0],newp[0],name)
     cursor.execute("""select credits from wallet where username=%s""",(name))
     cre=cursor.fetchone()
     cre[0]=cre[0]-last[1]
     cursor.execute("""update wallet set credits = %s where username =%s""",(cre[0],last[2]))

     conn.commit()
     conn.close()



@app.route("/sign_up")
def sign():
    return render_template('sign.html')


@app.route("/one",methods=["GET","POST"])
def first():
  #  conne=sqlite3.connect('auction.sqlite')
  #  cure=conne.cursor()
   
    name=request.form.get("user_name")
    passw=request.form.get("password")
    icheck()
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    email_id=request.form.get("email_id")
    ph_no=request.form.get("ph_no")
    conn = None
    conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
    cursor=conn.cursor()
    cursor.execute("use prj2")
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
      cursor.execute("""insert into user values (%s,%s,%s,%s,%s,%s)""",(first_name,last_name,ph_no,email_id,passw,name))
      cursor.execute("""insert into wallet values (%s,%s)""",(0,name))
      conn.commit()
      cursor.execute("""select * from product
left join 
(select avg(points),reci from rating group by reci) as p
on product.username=p.reci
where not exists(select * from purchase
					where product.id=purchase.productid)
""")
      products=cursor.fetchall()
      l=len(products)
      print(products)
      conn.close()
      if request.method == "GET":
        prodid=(int)(request.args.get("prodid"))
        addnotify(prodid)
      return render_template("options.html",products=products,l=l)
  
@app.route("/wallet",methods=["GET","POST"])
def wallet():
  conn = None
  icheck()
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password='')
  cursor=conn.cursor()
  cursor.execute("use prj2")
  print(name)
  cursor.execute("""select * from wallet where username = %s""",(name,))
  row=cursor.fetchall()
  print(row)
  for i in row:
    print(i)
    cr=i[0]
    print(cr)
  conn.close()
  return render_template("wallet.html",cr=cr)
@app.route("/listproduct",methods=["GET","POST"])
def listproduct():
  return render_template("form.html")
@app.route("/profile",methods=["GET","POST"])
def profile():
  global name
  conn = None
  icheck()
  conn = mysql.connector.connect(host='localhost',
                                        user='ayush',
                                        password= '')
  cursor=conn.cursor()
  cursor.execute("use prj2")
  if request.method == "GET":
    pts=(int)(request.args.get("point"))
    reca=(request.args.get("reci"))
    reca=(int)(reca)
    cursor.execute("select * from purchase left join product as p on purchase.productid=p.id where purchase.username =%s",(name,))
    pur=cursor.fetchall()
    reci=pur[reca-1][8]

    cursor.execute("""select * from rating where reci =%s and username =%s""",(reci,name))
    prev=cursor.fetchall()
    if prev is None:
      cursor.execute("""insert into rating values (%s,%s,%s)""",(pts,reci,name))
      conn.commit()
      t="rating recorded"
      return render_template("buf.html",t=t)
    else:
      cursor.execute("""update rating set points=%s where reci=%s and username =%s""",(pts,reci,name))
      conn.commit()
      t="updated rating"
      return render_template("buf.html",t=t)
  pur1=[]
  cursor.execute("""select * from user where user_name =%s""",(name,))
  details=cursor.fetchone()
  cursor.execute("select * from purchase left join product as p on purchase.productid=p.id where purchase.username =%s",(name,))
  pur=cursor.fetchall()
  for i in pur:
    pur1.append(list(i))
  s=len(pur1)
  cursor.execute("select * from product where username =%s and not exists(select * from purchase where purchase.productid=product.id)",(name,))
  onlis=cursor.fetchall()

  
  return render_template("profile.html",details=details,pur1=pur1,pur=pur,onlis=onlis,s=s)
@app.route("/addproduct",methods=["GET","POST"])
def addproduct():  
    conn = None
   

    icheck()
    conn = mysql.connector.connect(host='localhost',
                                        user='ayush',
                                        password= '')
    cursor=conn.cursor()
    cursor.execute("use prj2")
    cursor.execute("select * from product")
    rows=cursor.fetchall()
    for i in rows:
      pid=i[0]
    pid=pid+1
    print("in else")
    productname=request.form.get("product_name")
    productcategory=request.form.get("product_category")
    productprice=request.form.get("price")
    cursor.execute("""insert into product values (%s,%s,%s,%s,%s)""",(pid,productname,productcategory,productprice,name))
    conn.commit()
    cursor.execute("""select * from product
left join 
(select avg(points),reci from rating group by reci) as p
on product.username=p.reci
where not exists(select * from purchase
					where product.id=purchase.productid)
""")
    products=cursor.fetchall()
    l=len(products)
    conn.commit()
    conn.close()
    if request.method == "GET":
      prodid=(int)(request.args.get("prodid"))
      addnotify(prodid)
    return render_template("options.html",products=products,l=l)
@app.route("/current",methods=["GET","POST"])
def current():
  conn = None
  icheck()
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
  cursor=conn.cursor()
  global name
  cursor.execute("use prj2")
  cursor.execute("""select max(productid) from purchase""")
  maxi=cursor.fetchone()
  cursor.execute("""select productid from purchase where productid =%s""",(maxi))
  p_id=cursor.fetchone()
  cursor.execute("""select * from product
  left join 
  (select avg(points),reci from rating group by reci) as p
  on product.username=p.reci
  where product.id=%s""",(p_id) )
  value=cursor.fetchone()
  cursor.execute("""select max(amount) from bid where productid=%s group by productid""",(p_id))
  bamt=cursor.fetchone()
  cursor.execute("""select amount from bid where productid=%s""",(p_id))
  bs=cursor.fetchall()
 # print(name)
  cursor.execute("""select credits from wallet where username =%s""",(name,))
  wamt=cursor.fetchone()
  cursor.execute("select amount from bid where username=%s and productid=%s",(p_id[0],name))
  allbid=cursor.fetchall()
  dt=0
  for i in allbid:
    dt=dt+i[0]

  if wamt is not None:
    namt=wamt[0]-dt
  else:
    namt=0
  conn.commit()

  if request.method == "GET" and request.args.get("bida") is not None:
  #  print("in get")
    bida=(int)(request.args.get("bida"))
   # print(bida)
    if bida<namt and bida>bamt[0]:
      cursor.execute("""insert into bid values(current_timestamp(),%s,%s,%s)""", (bida,name,p_id[0]))
      conn.commit()
      conn.close()
      bamt=bida
      bs.append(bida)
      print("i if")
      namt=namt-bida
      print(value,bamt,bs,namt)
      return render_template("currentp.html",value=value,bamt=bamt,bs=bs,namt=namt)
  print(bamt)
  return render_template("currentp.html",value=value,bamt=bamt,bs=bs,namt=namt)
@app.route("/registerbid",methods=["GET","POST"])
#def registerbid():
 # print("in functiom")
  #print(request.values.get('input', ''))
 # return render_template("buf.html")
@app.route("/search",methods=["GET","POST"])
def search():
 # print("ins eaddd")
 # if request.form.get("pid") is not None:
  pi=""
  if request.form.get("pid"):
    pi=request.form.get("pid")
  pcategory=request.form.get("pcategory")
  pname=request.form.get("pname")
  print(pcategory+" is   "+pname)
  conn = None
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
  #if conn.is_connected():
  if request.method == "GET":
    prodid=(int)(request.args.get("prodid"))
    addnotify(prodid)
  cursor=conn.cursor()
  cursor.execute("use prj2")
  if pi :
    cursor.execute("""select * from product where id=%s""",(pi,))
    products=cursor.fetchone()
    conn.close()
    print(products)
    return render_template("options.html",products=products)
  if (pcategory) and (not pname):
    cursor.execute("""select * from product where category=%s """,(pcategory,))
    products=cursor.fetchall()
    l=len(products)
    conn.close()
    print(products)
    return render_template("options.html",products=products,l=l)
  if(not pcategory) and (pname):
    print("in if")
    cursor.execute("""select * from product where pname =%s""",(pname,))
    products=cursor.fetchall()
    conn.close()
    l=len(products)
    print(products)
    return render_template("options.html",products=products,l=l)
  if(pcategory) and (pname):
    cursor.execute("""select * from product where category=%s and pname=%s""",(pcategory,pname,))
    products=cursor.fetchall()
    conn.close()
    print(products)
    return render_template("options.html",products=products)
  


@app.route("/addcredit",methods=["GET","POST"])
def addcredit():
  toadd=request.form.get("adcredits")
  conn = None
  icheck()
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
  cursor=conn.cursor()
  cursor.execute("use prj2")
  cursor.execute("""select * from wallet where username = %s""",(name))
  row=cursor.fetchall()
  print(row)
  for i in row:
    print(i)
    cr=i[0]
  toaddin=(int)(toadd)
 # print(type(cr))
  #cr=(int)cr
  cr=cr+toaddin
  cursor.execute("""update wallet set credits=%s where username = %s""",(cr,name,))
  conn.commit()
  conn.close()
  return render_template("wallet.html",cr=cr)

@app.route("/feedback",methods=["GET","POST"])
def feedback():
  mat=request.form.get("rev")
  global name
  if request.method == "GET":
    prodid=(int)(request.args.get("prodid"))
    addnotify(prodid)
  client = MongoClient("127.0.0.1:27017")
  mydb=client['prj']
  mycol=mydb["feed"]
  mydict={"user":name,"review":mat}
  mycol.insert(mydict) 
  print("inserted")
  conn=None
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
  cursor=conn.cursor()
  cursor.execute("use prj2")
  cursor.execute("""select * from product
  left join 
  (select avg(points),reci from rating group by reci) as p
  on product.username=p.reci
  where not exists(select * from purchase
					where product.id=purchase.productid)
          """)
  products=cursor.fetchall()
  conn.commit()
  l=len(products)
  conn.close()
  return render_template("options.html",products=products,l=l)

def addnotify(prodid):
  print(name)
  conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '')
  cursor=conn.cursor()
  cursor.execute("use prj2")
  cursor.execute("""select emailid from user where user_name=%s """,("user",))
  e=cursor.fetchall()
  for i in e:
    email=i
  prodid=(int)(prodid)
  cursor.execute("""select * from product
  left join 
  (select avg(points),reci from rating group by reci) as p
  on product.username=p.reci
  where not exists(select * from purchase
					where product.id=purchase.productid)
          """)
  products=cursor.fetchall()
  realid=products[prodid-1][0]
  client = MongoClient("127.0.0.1:27017")
  mydb=client['prj']
  mycol=mydb["notific"]
  mydict={"mail":email,"prodid":realid}
  mycol.insert(mydict)
def sendm(em,prodid,name):
  content ="Auction is going to start"
  mail=smtplib.SMTP('smtp.gmail.com:587')
  mail.ehlo()
  mail.starttls()
  mail.login('fromemail','passw')
  mail.sendmail('fromemail',prodid,content)
  mail.close

#@socketio.on('message')
#def handleMessage(msg):
 # current()
  #global name
  #print("executed current")
  #send(msg,broadcast=True)
