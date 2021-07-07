from flask import Flask
from datetime import datetime
from flask import jsonify, render_template, request
import mysql.connector
from pymongo import MongoClient
from flask_socketio import SocketIO
import os
app = Flask(__name__)
socketio = SocketIO(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
@app.route('/')
def login():
    return render_template('login.html')


def connect():
    conn = None
    conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '9290827021')
    return conn


@app.route("/check",methods=["POST"])
def check():
  global name
  username=request.form.get("user_name")
  passw=request.form.get("password")
  conn=connect()
  cursor=conn.cursor()
  cursor.execute("use prj2")
  cursor.execute("select * from user")
  row=cursor.fetchall()
  for i in row:
    if (i[0]==username):
      if(i[1]==passw):
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
          conn.close()
          return render_template("products.html",products=products,l=l,username=username)
  conn.close()
  msg="Login failed"
  return render_template('login.html',msg=msg)

@app.route("/sign_up")
def sign():
    return render_template('sign.html')

@app.route("/register",methods=["POST"])
def register():
    username=request.form.get("user_name")
    passw=request.form.get("password")
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    email_id=request.form.get("email_id")
    ph_no=request.form.get("ph_no")
    conn = connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    cursor.execute("select * from user")
    row=cursor.fetchall()
    flag=0
    for r in row:
        if(r[0] == username):
            flag=1
            break
        if(r[4] == email_id):
            flag=1
            break
        if(r[5] == ph_no):
            flag=1
            break
    if flag == 1:
        conn.close()
        msg="user exists"
        return render_template("login.html",msg=msg)
    else:
      cursor.execute("""insert into user values (%s,%s,%s,%s,%s,%s)""",(first_name,last_name,ph_no,email_id,passw,username))
      cursor.execute("""insert into wallet values (%s,%s)""",(0,username))
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
    return render_template("products.html",products=products,l=l,username=username)


@app.route("/<username>/wallet",methods=["POST"])
def wallet(username):
    conn = connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    cursor.execute("""select * from wallet where username = %s""",(username,))
    row=cursor.fetchall()
    for i in row:
        cr=i[0]
    conn.close()
    return render_template("wallet.html",cr=cr,username=username)


@app.route("/<username>/updatedwallet",methods=["POST"])
def addcredit(username):
    toadd=request.form.get("adcredits")
    conn = connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    cursor.execute("""select * from wallet where username = %s""",(username,))
    row=cursor.fetchall()
    for i in row:
        cr=i[0]
    toaddin=(int)(toadd)
    cr=int(cr)+int(toaddin)
    cursor.execute("""update wallet set credits=%s where username = %s""",(cr,username,))
    conn.commit()
    conn.close()
    return render_template("wallet.html",cr=cr,username=username)


@app.route("/<username>/search",methods=["POST"])
def search(username):
    pi=""
    pi=request.form.get("pid")
    pcategory=request.form.get("pcategory")
    pname=request.form.get("pname")
    conn = connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    if pi :
        cursor.execute("""select * from product where id=%s""",(pi,))
        products=cursor.fetchone()
        conn.close()
        return render_template("products.html",products=products,username=username)
    if (pcategory) and (not pname):
        cursor.execute("""select * from product where category=%s """,(pcategory,))
        products=cursor.fetchall()
        l=len(products)
        conn.close()
        return render_template("products.html",products=products,username=username)
    if(not pcategory) and (pname):
        cursor.execute("""select * from product where pname =%s""",(pname,))
        products=cursor.fetchall()
        conn.close()
        l=len(products)
        return render_template("products.html",products=products,username=username)
    if(pcategory) and (pname):
        cursor.execute("""select * from product where category=%s and pname=%s""",(pcategory,pname,))
        products=cursor.fetchall()
        conn.close()
        return render_template("products.html",products=products,username=username)
    return render_template("products.html",products=products,username=username)

@app.route("/<username>/products",methods=["POST"])
def displayproducts(username):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute("""use prj2""")
    cursor.execute("""select * from product
    left join 
    (select avg(points),reci from rating group by reci) as p
    on product.username=p.reci
    where not exists(select * from purchase
    where product.id=purchase.productid)
    """)
    products=cursor.fetchall()
    l=len(products)
    conn.close()
    return render_template("products.html",products=products,l=l,username=username)


@app.route("/<username>/listproduct",methods=["GET","POST"])
def listproduct(username):
  return render_template("form.html",username=username)

@app.route("/<username>/addproduct",methods=["POST"])
def addproduct(username):  
    conn = connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    cursor.execute("select * from product")
    rows=cursor.fetchall()
    for i in rows:
      pid=i[0]
    pid=pid+1
    productname=request.form.get("product_name")
    productcategory=request.form.get("product_category")
    productprice=request.form.get("price")
    cursor.execute("""insert into product values (%s,%s,%s,%s,%s)""",(pid,productname,productcategory,productprice,username))
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
    return render_template("products.html",products=products,l=l,username=username)

@app.route("/<username>",methods=["POST"])
def profile(username):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    pur1=[]
    cursor.execute("""select * from user where user_name =%s""",(username,))
    details=cursor.fetchone()
    cursor.execute("select * from purchase left join product as p on purchase.productid=p.id where purchase.username =%s",(username,))
    pur=cursor.fetchall()
    for i in pur:
        pur1.append(list(i))
    s=len(pur1)
    cursor.execute("select * from product where username =%s and not exists(select * from purchase where purchase.productid=product.id)",(username,))
    onlis=cursor.fetchall()
    conn.close()
    return render_template("profilenew.html",details=details,pur1=pur1,pur=pur,onlis=onlis,s=s,username=username)

@app.route("/<username>/rate",methods=["POST"])
def rate(username):
    conn=connect()
    cursor=conn.cursor()
    pts=(int)(request.args.get("point"))
    reca=(request.args.get("reci"))
    reca=(int)(reca)
    cursor.execute("select * from purchase left join product as p on purchase.productid=p.id where purchase.username =%s",(username,))
    pur=cursor.fetchall()
    reci=pur[reca-1][8]
    cursor.execute("""select * from rating where reci =%s and username =%s""",(reci,username))
    prev=cursor.fetchall()
    if prev is None:
      cursor.execute("""insert into rating values (%s,%s,%s)""",(pts,reci,username))
      conn.commit()
      t="rating recorded"
      conn.close()
      return render_template("buf.html",t=t)
    else:
      cursor.execute("""update rating set points=%s where reci=%s and username =%s""",(pts,reci,username))
      conn.commit()
      t="updated rating"
      conn.close()
      return render_template("buf.html",t=t)
      pur1=[]
      cursor.execute("""select * from user where user_name =%s""",(username,))
      details=cursor.fetchone()
      cursor.execute("select * from purchase left join product as p on purchase.productid=p.id where purchase.username =%s",(username,))
      pur=cursor.fetchall()
      for i in pur:
          pur1.append(list(i))
    s=len(pur1)
    cursor.execute("select * from product where username =%s and not exists(select * from purchase where purchase.productid=product.id)",(username,))
    onlis=cursor.fetchall()
    return render_template("profile.html",details=details,pur1=pur1,pur=pur,onlis=onlis,s=s,username=username)

def connectm():
    client = MongoClient("127.0.0.1:27017")
    mydb=client['prj']
    return mydb


@app.route("/<username>/feedback",methods=["POST"])
def feedback(username):
  mat=request.form.get("rev")
  mydb=connectm()
  mycol=mydb["feed"]
  mydict={"user":username,"review":mat}
  mycol.insert(mydict) 
  print("inserted")
  conn=connect()
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
  return render_template("products.html",products=products,l=l,username=username)

@app.route("/<username>/notify",methods=["POST"])
def addnotify(username):
    conn = connect()
    cursor=conn.cursor()
    cursor.execute("use prj2")
    cursor.execute("""select emailid from user where user_name=%s """,(username,))
    e=cursor.fetchall()
    for i in e:
        email=i
    prodid=request.form.get("prodid")
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
    mydb=connectm()
    mycol=mydb["notific"]
    mydict={"mail":email,"prodid":realid}
    mycol.insert(mydict)
    conn = mysql.connector.connect(host='localhost',
                                       user='ayush',
                                       password= '9290827021')
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
    return render_template('products.html',products=products,l=l,username=username)

@app.route("/<username>/current",methods=["GET","POST"])
def current(username):
    conn = connect()
    print(username)
    cursor=conn.cursor()
    name=username
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
    conn.close()
    return render_template("current.html",value=value,bamt=bamt,bs=bs,namt=namt,username=username)

@app.route("/<username>/current/register",methods=["POST"])
def registerbid(username):
    conn=connect()
    cursor=conn.cursor()
    name=username
    bida=(int)(request.form.get("bida"))
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
    if bida<namt and bida>bamt[0]:
      cursor.execute("""insert into bid values(current_timestamp(),%s,%s,%s)""", (bida,name,p_id[0]))
      conn.commit()
      conn.close()
      bamt=bida
      bs.append(bida)
      namt=namt-bida
      return render_template("current.html",value=value,bamt=bamt,bs=bs,namt=namt,username=username)

@socketio.on('my event')
def handle_my_custom_event( json,methods=['GET', 'POST']):
    print('received my event: ')
    conn=connect()
    cursor=conn.cursor()
    bida=(int)(json["message"])
    name=json["user_name"]
    username=name
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
    if bida<namt and bida>bamt[0]:
      cursor.execute("""insert into bid values(current_timestamp(),%s,%s,%s)""", (bida,name,p_id[0]))
      conn.commit()
      conn.close()
      bamt=bida
      bs.append(bida)
      namt=namt-bida
    print(json)
    socketio.emit('my response',json)

@socketio.on('refr')
def refr(username):
    print("in refr")
    current(username["username"])

if __name__ == '__main__':
    socketio.run(app, debug=True)