from flask import Flask,render_template,request,make_response,send_from_directory,session
import mysql.connector
from mysql.connector import Error
import threading
import datetime
from datetime import timedelta
import os
import json
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO,emit
import urllib.request
import urllib.parse
import getpass
import pymongo
import requests
import smtplib
from elasticsearch import Elasticsearch  
import threading
import time
sem=threading.Semaphore()
# set FLASK_APP=main.py
# python -m flask run
#/home/ayush/Documents/online-auction-system-hadithya369-patch-2/DBMS Project
# /home/ayush/Desktop/lab/DBMS Project
UPLOAD_FOLDER = "/home/ayush/Desktop/lab/DBMS Project/static"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

CONNECTED_NODE_ADDRESS = "http://0.0.0.0:8080"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


uname='ayush'
pswd='9290827021'
CONNECTED_NODE_ADDRESS1 = "http://0.0.0.0:8081"
print('new')

def comp_auct(msg):
    print('comp auct called : received msg ' + msg)
    msg=str(msg)
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select user.username,product.prodname,email,amt,tim from bids,user,product where user.username=bids.username and product.prodid=bids.prodid and amt in (select max(amt) from bids where prodid='"+msg+"')"
            cursor.execute(qstring)
            record=cursor.fetchall()
            print(record[0])
            qstring="select username from lists where prodid='"+msg+"'"
            cursor.execute(qstring)
            sel=(cursor.fetchall())[0][0]
            sel=str(sel)
            qstring="update wallet set credits=credits+"+str(record[0][3])+" where username='"+sel+"'"
            cursor.execute(qstring)
            qstring="update wallet set credits=credits-"+str(record[0][3])+" where username='"+str(record[0][0])+"'"
            cursor.execute(qstring)
            qstring="""insert into purchases values(%s,%s,%s,%s)"""
            print("#######inserted into purchases#####")
            
           # cursor.execute(qstring,(str(record[0][0]),msg))
          #  qstring="""insert into purchases values(%s,%s,%s)"""
            cursor.execute(qstring,(str(record[0][0]),msg,str(record[0][4]),str(record[0][3])))
            print("###inserted #####into purchase")
            s_mail('Product Purchased','Congrats!!!! You have won the bid war for the following prduct \nName : '+record[0][1],record[0][2])
            con.commit()
            cursor.close()
            con.close()
        else:
            return
        # curt=datetime.datetime.now()
        # uct=datetime.datetime(int(pst[:4]),int(pst[5:7]),int(pst[8:10]),int(pst[11:13]),int(pst[14:16]),int(pst[17:19]))
    except Error as Er:
        print(Er)
    post_object = {
        'Buyer':record[0][0],
        'Seller':sel,
        'Productid':msg,
        'price':record[0][3],
        }
    print(post_object)
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
    requests.post(new_tx_address,json=post_object,headers={'Content-type': 'application/json'})
    response=requests.get("{}/mine".format(CONNECTED_NODE_ADDRESS))
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS1)
    requests.post(new_tx_address,json=post_object,headers={'Content-type': 'application/json'})
    response=requests.get("{}/mine".format(CONNECTED_NODE_ADDRESS1))
    print(response)

def ch():
    curt=str(datetime.datetime.now())[:19]
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from lists where endate > '"+curt+"'"
            cursor.execute(qstring)
            record=cursor.fetchall()
            print(record)
            for el in record:
                pen=str(el[2])
                curt=datetime.datetime.now()
                uct=datetime.datetime(int(pen[:4]),int(pen[5:7]),int(pen[8:10]),int(pen[11:13]),int(pen[14:16]),int(pen[17:19]))
                threading.Timer((uct-curt).total_seconds(),comp_auct,args=[str(el[0])]).start()
                print('started '+el[0]+' time '+str((uct-curt).total_seconds()))
            cursor.close()
            con.close()
        else:
            return
    except Error as Er:
        print(Er)
ch()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():
    return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login_check():
    curt=str(datetime.datetime.now())[:19]
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            cursor.execute("""select product.prodid,prodname,category,prodprice, count(*) from product,un,lists where product.prodid=un.prodid and lists.prodid=product.prodid and endate> %s group by product.prodid having count(*) > 1 order by count(*) desc""",(curt,))
            record1= cursor.fetchall()
            print('record1')
            print(record1)
            cursor.close()
            con.close()
    except Exception as Ex:
        print(Ex)
    username=request.form.get('user')
    pswd1=request.form.get('password')
    verif=0
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring='select * from user where username= "'+username+'"'
            cursor.execute(qstring)
            record=cursor.fetchall()
            verif=5
            for el in record:
                print(el[5])
                if el[5] == pswd1:
                    verif=1
                else:
                    verif=0
            print(verif)
            cursor.close()
            con.close()
            print('closed database')
            if verif == 1:
                resp =make_response( render_template('Homepage.html',pop=record1,sb=0))
                session['username']=username
                return resp
            else:
                return render_template('login.html',erm='Wrong Username or Password')
    except Error as Er:
        print(Er)

def chkdat(stdat,endat):
    tbr=True
    curt=datetime.datetime.now()
    pen=stdat
    uct=datetime.datetime(int(pen[:4]),int(pen[5:7]),int(pen[8:10]),int(pen[11:13]),int(pen[14:16]),int(pen[17:19]))
    if (curt>uct):
        if abs((uct-curt).total_seconds()) > 1:
            tbr=False
    con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
    if con.is_connected():
        print('connected')
        cursor=con.cursor()
        qstring="select * from lists where '"+stdat+"' between stdate and endate"
        cursor.execute(qstring)
        record=cursor.fetchall()
        if record!=[]:
            tbr=False
        qstring="select * from lists where '"+endat+"' between stdate and endate"
        cursor.execute(qstring)
        record=cursor.fetchall()
        if record!=[]:
            tbr=False
        cursor.close()
        con.close()
        if (str(stdat))>=(str(endat)):
            tbr=False
    return tbr

@app.route('/wallet_pg',methods=['POST','GET'])
def wallet_pg():
    wuser=str(session['username'])
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from wallet where username='"+wuser+"'"
            cursor.execute(qstring)
            record=cursor.fetchall()
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    return render_template('wallet.html',mon=record[0][1])

@app.route('/wallet',methods=['POST','GET'])
def add_credit():
    wuser=session['username']
    amt=str(request.form.get('amt'))
    print(wuser)
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from user where username='"+wuser+"'"
            cursor.execute(qstring)
            record=cursor.fetchall()
            un=str(record[0][0])
            cursor.execute("""select credits from wallet where username=%s""",(wuser,))
            r1=cursor.fetchall()
            r1=str(r1[0][0])
            print('uuuuuunnnnnn'+un)
            if len(record)!=0:
                qstring="insert into credpass (username,amt) values ('"+un+"','"+amt+"')"
                cursor.execute(qstring)   
                con.commit()
                cursor.execute("""select idd,email from credpass,user where user.username=credpass.username and credpass.username=%s and amt=%s""",(un,str(amt),))
                record=cursor.fetchall()
                s_mail('Transaction id',str(record[0][0]),str(record[0][1]))
            else:
                wuser=''
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    if wuser=='':
        return render_template('wallet.html',ermsg='Couldnt find User',mon='0')
    else:
        return render_template('wallet.html',mon=r1)

@app.route('/get_wallet',methods=['POST','GET'])
def get_wallet():
    wuser=session['username']
    passcode=str(request.form.get('passcode'))
    print(wuser+'pass'+passcode)
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from credpass where idd= "+passcode
            cursor.execute(qstring)
            record=cursor.fetchall()
            # qstring="select * from wallet where username='"+wuser+"';"
            cursor.execute("""select * from wallet where username=%s """,(wuser,))
            record1=cursor.fetchall()
            cr=int(str(record1[0][1]))
            if len(record)!=0:
                otherv=str(cr+int(record[0][2]))
                # qstring="update wallet set credits = "+str(cr+int(str(un[2])))+"where username= '"+str(un[0])+"'"
                cursor.execute("""update wallet set credits = %s where username=%s""",(otherv,record[0][0],))   
                cursor.execute("""delete from credpass where idd=%s""",(passcode,))
                con.commit()
            else:
                wuser=''
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    if wuser=='':
        return render_template('wallet.html',ermsg='Enter Valid Passcode',mon=cr)
    else:
        return render_template('wallet.html',mon=otherv)
                  
@app.route('/cur_auction',methods=['POST','GET'])
def cur_auction():
    curt=str(datetime.datetime.now())[:19]
    print('curt:'+curt+'|')
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select prodname,prodprice,proddes,category,product.prodid,endate from product,lists where product.prodid=lists.prodid and '"+curt+"' between lists.stdate and lists.endate"
            cursor.execute(qstring)
            record=cursor.fetchall()
            if record==[]:
                print('base')
                cursor.close()
                con.close()
                return render_template('nocurrauct.html')
            qstring="select amt,username from bids where prodid = '"+str(record[0][4])+"' order by amt"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            cursor.close()
            con.close()
            print(record)
            print('notbase')
            te=str(record[0][5])
            endtime=te[0:4]+","+str(int(te[5:7])-1)+","+te[8:10]+","+te[11:13]+","+te[14:16]+","+te[17:19]+",00"
            print('eeee'+endtime+'eeee')

            myclient=pymongo.MongoClient('mongodb://localhost:27017/')
            mydb=myclient["oas"]
            mycol=mydb["imgf"]
            mydict={'pid':str(record[0][4])}
            x=mycol.find(mydict)
            all_img=[]
            for xx in x:
                print(xx['iarr'])
                all_img=xx['iarr']
            county=0
            countyar=[]
            for im in all_img:
                county=county+1
                countyar.append(county)
            myclient.close()
            return render_template('currentauction.html',proname=record[0][0],proprice=record[0][1],prodes=record[0][2],procat=record[0][3],proid=record[0][4],initial=record1,endtimes=endtime,allimg=all_img,car=countyar,carno=county)
            # curt=datetime.datetime.now()
            # uct=datetime.datetime(int(pst[:4]),int(pst[5:7]),int(pst[8:10]),int(pst[11:13]),int(pst[14:16]),int(pst[17:19]))
    except Error as Er:
        print(Er)
   # return render_template('currentauction.html')
#2019-12-10 09:30:00
#0123456789012345678
@app.route('/enlist_pr',methods=['POST','GET'])
def enlist_pr():
    return render_template('enlistproduct.html')

@app.route('/',methods=['POST','GET'])
def logout():
    resp=make_response(render_template('login.html'))
    session.pop('username',None)
    return resp

def we(dur,wamt):
    cst=0
    if dur==2:
        cst=200
    elif dur==6:
        cst=800
    elif dur==24:
        cst=3000
    else:
        cst=6000
    if wamt<cst:
        return [False,0]
    return [True,cst]

@app.route('/enlist',methods=['POST','GET'])
def enlist():
    curt=str(datetime.datetime.now())[:19]
    print('curt:'+curt+'|')
    pname=request.form.get('pname')
    pprice=request.form.get('pprice')
    pdes=request.form.get('pdes')
    dhr=request.form.get('rn1')
    print('dhr '+dhr)
    pst=request.form.get('stdat')+' '+request.form.get('sttim')+':00'
    # pen=request.form.get('endat')+' '+request.form.get('entim')+":00"
    pstco=datetime.datetime(int(pst[:4]),int(pst[5:7]),int(pst[8:10]),int(pst[11:13]),int(pst[14:16]),int(pst[17:19]))+timedelta(minutes=int(dhr))
    pen=str(pstco)
    print('pst-----'+pst+'pen-----'+pen)
    pcat=request.form.get('pcat')
    us=str(session['username'])
   # sem.acquire()
    if chkdat(pst,pen)==False:
        return render_template('enlistproduct.html',ermsg='Try for different time slot')
   # sem.release()
    if 'file' not in request.files:
        print('No file part')
    file = request.files.getlist('file')
 #   index =1
 #   for f in file:
 #       filenam =f.filename
 #       filenam=str(pname[0]+pst)+str(index)+".jpg"
 #       index=index+1
 #       print('file'+filenam)
    myclient=pymongo.MongoClient('mongodb://localhost:27017/')
    mydb=myclient["oas"]
    mycol=mydb["imgf"]
    fnames=[]
    index=1
    for f in file:
        filenam = secure_filename(f.filename)
        filenam=str(pname[0]+pst)+str(index)+".jpg"
        print('file'+filenam)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filenam))
        fnames.append(filenam)
        index=index+1
    mydict={'pid':str(pname[0]+pst),'iarr':fnames}
    mycol.insert(mydict)
    myclient.close()
    # for f in file:

        # if user does not select file, browser also
        # submit an empty part without filename
    # if file.filename == '':
    #     print('No selected file')
    # if file and allowed_file(file.filename):
 #   if chkdat(pst,pen)==False:
 #       return render_template('enlistproduct.html',ermsg='Try for different time slot')
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            cursor.execute("""select * from wallet where username=%s""",(us,))
            record=cursor.fetchall()
            wamt=record[0][1]
            if we(int(dhr),int(wamt))[0]==False:
                print('not en cred')
                cursor.close()
                con.close()
                return render_template('enlistproduct.html',ermsg='Not enough Credits') 
            qstring="""insert into product values(%s,%s,%s,%s,%s)"""
            cursor.execute(qstring,(pname[0]+pst,pname,pprice,pdes,pcat))
            qstring="""insert into lists values(%s,%s,%s,%s)"""
   #         cursor.execute(qstring,(us,pname[0]+pst))
    #        qstring="""insert into lists values(%s,%s,%s)"""
            cursor.execute(qstring,(us,pname[0]+pst,pst,pen))
            con.commit()
            qstring="""insert into bids values(%s,%s,%s,%s)"""
            cursor.execute(qstring,(session['username'],pname[0]+pst,curt,pprice))
            cutprice=int(wamt)-we(int(dhr),int(wamt))[1]
            cursor.execute("""update wallet set credits=%s where username=%s""",(str(cutprice),session['username'],))
            cursor.execute("""insert into elas(prodid) values (%s)""",(pname[0]+pst,))
            cursor.execute("""select id from elas where prodid= %s """,(pname[0]+pst,))
            tempvar=int(cursor.fetchall()[0][0])
            curt=datetime.datetime.now()
            uct=datetime.datetime(int(pen[:4]),int(pen[5:7]),int(pen[8:10]),int(pen[11:13]),int(pen[14:16]),int(pen[17:19]))
            threading.Timer((uct-curt).total_seconds(),comp_auct,args=[str(pname[0]+pst)]).start()
            print('started '+pname[0]+pst+' time '+str((uct-curt).total_seconds()))
            con.commit()
            cursor.close()
            con.close()
            
            mdc={'name':pname,'price':pprice,'description':pdes,'category':pcat,'seller':session['username'],'stdate':pst,'endate':pen}
            print('mdc')
            print(mdc)                                                                          
            es=Elasticsearch(HOST='http://localhost',PORT='9200')
            es.index(index='pr1',doc_type='Goods',id=tempvar,body=mdc)
    except Error as Er:
        print(Er)

    return render_template('enlistproduct.html')
#2019-12-10 09:30:00
#0123456789012345678

@app.route('/signup',methods=['POST',"GET"])
def signup():
    return render_template('signup.html')

@app.route('/register',methods=['POST',"GET"])
def register():
    nus=request.form.get('uname')
    fn=request.form.get('fname')
    ln=request.form.get('lname')
    emai=request.form.get('emai')
    phone=request.form.get('phone')
    pswdd=request.form.get('pswd')
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            cursor.execute("""select * from user where username=%s""",(nus,))
            record=cursor.fetchall()
            if(len(record)!=0):
                return render_template('signup.html',errm='User already exists')
            else:
                cursor.execute("""insert into user values(%s,%s,%s,%s,%s,%s)""",(nus,fn,ln,phone,emai,pswdd,))
                cursor.execute("""insert into wallet values(%s,%s)""",(nus,'0',))
                con.commit()
                return render_template('login.html')
            cursor.close()
            con.close()
        else:
            print('not conn')
    except Error as Er:
        print(Er)
        print('not conn')

@app.route('/profile')
def get_prof():
    uprof=str(session['username'])
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            print(uprof)
            qstring="select * from user where username='"+uprof+"';"
            cursor.execute(qstring)
            rec1=cursor.fetchall()
            qstring="select product.prodid,prodname,category,prodprice from lists,product where lists.prodid=product.prodid and username='"+uprof+"';"
            cursor.execute(qstring)
            rec=cursor.fetchall()
            #qstring="select purchases.prodid,prodname,category,prodprice,amount,rnot from purchases,product,lists where purchases.prodid=product.prodid and lists.prodid=product.prodid and lists.username <> purchases.username  and purchases.username='"+uprof+"';"
            qstring="select purchases.prodid,prodname,category,prodprice,amount from purchases,product,lists where purchases.prodid=product.prodid and lists.prodid=product.prodid and lists.username <> purchases.username  and purchases.username='"+uprof+"';"
            cursor.execute(qstring)
            rec2=cursor.fetchall()
            myclient=pymongo.MongoClient('mongodb://localhost:27017/')
            mydb=myclient["oas"]
            mycol=mydb["review"]
            rec2l=[]
            for z in rec2:
                rec2l.append(list(z))
            for z in rec2l:
                mydict={"pid":z[0]}
                x=mycol.find(mydict)
                print(x)
                rvaluex=0
                for elemer in x:
                    rvaluex=1
                z.append(rvaluex)
            print("rec2")
            print(rec2l)
            rec2 = [tuple(l) for l in rec2l]
            myclient.close()
            qstring="select prodid from lists where username='"+uprof+"';"
            cursor.execute(qstring)
            nsd=cursor.fetchall()
            cursor.close()
            con.close()
            try :
                myclient=pymongo.MongoClient('mongodb://localhost:27017/')
                mydb=myclient["oas"]
                mycol=mydb["review"]
                srat=0
                ct=0
                for el in nsd:
                    print(el)
                    quer={"pid":str(el[0])}
                    print(quer)
                    x=mycol.find(quer)
                    for temp in x:
                        print(temp)
                        srat=srat+int(temp['rno'])
                        ct=ct+1
                if ct==0:
                    srat='N/A'
                else:
                    srat=int(srat)/int(ct)
                myclient.close()
            except Exception as Er:
                print(Er)
        return render_template('profile.html',rec1=rec1,rec=rec,rec2=rec2,srat=srat)
    except Error as Er:
        print(Er)

def brmo(myqu):
    myqu=myqu.split()
    if(len(myqu)==0):
        return ''
    else:
        ans=''
        for st in myqu:
            ans=ans+'*'+st+'* '
        return ans

    
@app.route('/home',methods=['GET','POST'])
def home_pg():
    curt=str(datetime.datetime.now())[:19]
    sb=0
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            cursor.execute("""select product.prodid,prodname,category,prodprice, count(*) from product,un,lists where product.prodid=un.prodid and lists.prodid=product.prodid and endate> %s group by product.prodid having count(*) > 1 order by count(*) desc""",(curt,))
            record1= cursor.fetchall()
            print('record1')
            print(record1)
            cursor.close()
            con.close()
    except Exception as Ex:
        print(Ex)
    if request.method!='POST':
        return render_template('Homepage.html',pop=record1,sb=sb)
    try:
        myquery=str(request.form.get('myquery'))
        if len(myquery)==0:
            sb=0
        else:
            sb=1
        print('no exce'+myquery)                               
        es=Elasticsearch(HOST='http://localhost',PORT='9200')
        res2=es.search(index='pr1',body={'from':0,'size':5,'query':{
                'query_string':{
                    'query':myquery,
                    'fields':['name^8','category^6','seller^5','price^4','description^4','stdate^2','endate^2']
                 }
        }})
        myd=[]
        for el in res2['hits']['hits']:
            myd.append([el['_id'],el['_score']])
        print(myd)
        myd=sorted(myd,key=lambda x:-1*x[1])
        print(myd)
        st=set([])
        ar=[]
        for el in myd:
            if el[0] not in st:
                ar.append(el[0])
                st.add(el[0])
        print(ar)
        if(len(ar)<5):
            myquery=brmo(myquery)
            print(myquery)
            res2=es.search(index='pr1',body={'from':0,'size':5,'query':{
                'query_string':{
                    'query':myquery,
                    'fields':['name^8','category^6','seller^5','price^4','description^4','stdate^2','endate^2']
                 }
            }})
            myd=[]


            for el in res2['hits']['hits']:
                myd.append([el['_id'],el['_score']])
            print(myd)
            myd=sorted(myd,key=lambda x:-1*x[1])
            print(myd)
            for el in myd:
                if el[0] not in st:
                    ar.append(el[0])
                    st.add(el[0])
            print('ar is')
            print(ar)
        if len(ar)==0:
            print("fuzzy")
            res3=es.search(index='pr1',body={'from':0,'size':5,'query':{
                'multi_match':{
                    'query':myquery+'~',
                    'fields':['name^8','category^6','seller^5','price^4','description^4','stdate^2','endate^2'],
                    'fuzziness':'AUTO'
                 
                 }
            }})
            for el in res3['hits']['hits']:
                myd.append([el['_id'],el['_score']])
            print(myd)
            myd=sorted(myd,key=lambda x:-1*x[1])
            print(myd)
            for el in myd:
                if el[0] not in st:
                    ar.append(el[0])
                    st.add(el[0])
            print('ar is')
            print(ar)

        try :
            con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
            if con.is_connected():
                print('connected')
                cursor=con.cursor()
                finrec=[]
                for nums in ar:
                    print(nums)
                    cursor.execute("select product.prodid,prodname,category,prodprice from product,elas where product.prodid=elas.prodid and id="+str(int(nums)))
                    record=(cursor.fetchall())
                    print(record)
                    if(len(record)==0):
                        continue
                    finrec.append(record[0])
                cursor.execute("""select product.prodid,prodname,category,prodprice, count(*) from product,un,lists where product.prodid=un.prodid and lists.prodid=product.prodid and endate> %s group by product.prodid having count(*) > 1 order by count(*) desc""",(curt,))
                record1= cursor.fetchall()
                print('record1')
                print(record1)
                cursor.close()
                con.close()
        except Error as Er:
            print(Er)
        return render_template('Homepage.html',finrec=finrec,pop=record1,sb=sb)
    except Exception as Ex:
        print(Ex)
        return render_template('Homepage.html',pop=record1,sb=sb)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

def get_c_p():
    curt=str(datetime.datetime.now())[:19]
    print('curt:'+curt+'|')
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select prodid from lists where '"+curt+"' between lists.stdate and lists.endate"
            cursor.execute(qstring)
            record=cursor.fetchall()
            cursor.close()
            con.close()
            if(len(record)!=0):
                return record[0][0]
    except Error as Er:
        print(Er)
    return [['-1']]

@socketio.on('chat message',namespace='/')
def chat_message(msg):
    print('received : ' + msg+'msg1')
    curt=str(datetime.datetime.now())[:19]
    print('curt:'+curt+'|')
    gcp=get_c_p()
    if(gcp[0][0]=='-1'):
        print('render in sio')
        emit('refr','abc',namespace='/')
        return
    if(str(msg).isdigit()) :
        try :
            con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
            if con.is_connected():
                print('connected')
                cursor=con.cursor()
                qstring="select credits from wallet where username='"+session['username']+"'"
                cursor.execute(qstring)
                record=cursor.fetchall()
                wallamt=record[0][0]
                if(int(wallamt)<int(msg)):
                    emit('not enough','not enough credits',namespace='/')
                else:
                    qstring="select max(amt) from bids where prodid='"+gcp+"'"
                    cursor.execute(qstring)
                    record=cursor.fetchall()
                    if(int(msg)>int(record[0][0])):
                        qstring="""insert into bids values(%s,%s,%s,%s)"""
                        cursor.execute(qstring,(session['username'],get_c_p(),curt,msg))
                        con.commit()
                        msg=session['username']+' bid '+msg
                        emit('chat message response',msg,broadcast=True,namespace='/')
                    else:
                        emit('not enough','bid higher',namespace='/')
                cursor.close()
                con.close()
            else:
                return
            # curt=datetime.datetime.now()
            # uct=datetime.datetime(int(pst[:4]),int(pst[5:7]),int(pst[8:10]),int(pst[11:13]),int(pst[14:16]),int(pst[17:19]))
        except Error as Er:
            print(Er)

@app.route('/mno')
def mno():
    url='http://localhost:5001/a'
    values = {'q' : 'python programming tutorials'}
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8') # data should be bytes
    req = urllib.request.Request(url, data)
    resp=urllib.request.urlopen(req)
    respData=resp.read()
    return str(respData)

@app.route('/product',methods=['GET','POST'])
def disp_prod():
    curt=str(datetime.datetime.now())[:19]
    disppr=request.form.get('pid')
    disppr=str(disppr)
    print('required--'+disppr)
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from product where prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record=cursor.fetchall()
            qstring="select username from lists where prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            sid=record1[0][0]
            qstring="select stdate,endate from lists where prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            std=record1[0][0]
            end=record1[0][1]
            qstring="select username,amount from purchases where  purchases.prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            notbut=1
            if(len(record1)==0):
                buy='N/A'
                buyc='N/A'
                print('aaaaaaaaaaaaaaaaaaa')
                notbut=1
            else:
                buy=str(record1[0][0])
                buyc=str(record1[0][1])
                print('bbbbbbbbbbbbbbbbbbbb')
                notbut=0
            if (str(std)<curt):
                print('ccccccccccccccccccc')
                notbut=0
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    myclient=pymongo.MongoClient('mongodb://localhost:27017/')
    mydb=myclient["oas"]
    mycol=mydb["imgf"]
    mydict={'pid':str(disppr)}
    x=mycol.find(mydict)
    all_img=[]
    for xx in x:
        print(xx['iarr'])
        all_img=xx['iarr']
    county=0
    countyar=[]
    for im in all_img:
        county=county+1
        countyar.append(county)
   
    myclient.close()
    myclient=pymongo.MongoClient('mongodb://localhost:27017/')
    mydb=myclient["oas"]
    mycol=mydb["review"]
    mydict={'pid':str(disppr)}
    x=mycol.find(mydict)
    rev="N/A"
    rno='N/A'
    for y in x:
        rev=y['rval']
        rno=y['rno']
    myclient.close()
    myclient=pymongo.MongoClient('mongodb://localhost:27017/')
    mydb=myclient["oas"]
    mycol=mydb["notify"]
    mydict={'username':session['username'],'pid':str(disppr)}
    x=mycol.find(mydict)
    print('x-----------')
    for xx in x:
        print('ddddddddddddddddd')
        notbut=0
    myclient.close()
    if sid==buy:
        buy="unsold"
    return render_template('prodpage.html',rec=record[0],sid=sid,std=std,end=end,buy=buy,buyc=buyc,allimg=all_img,car=countyar,carno=county,notbut=notbut,rev=rev,rno=rno)

@app.route('/review',methods=['GET','POST'])
def give_rev():
    return render_template('rev.html',pid=str(request.form.get('pid')))

def s_mail(sub,msg,mid):
    try:
        serv=smtplib.SMTP('smtp.gmail.com:587')
        serv.ehlo()
        serv.starttls()
        serv.login('ayush.astra@gmail.com','9290827021')
        finmsg='Subject: {} \n\n{}'.format(sub,msg)
        serv.sendmail('ayush.astra@gmail.com',mid,finmsg)
        serv.quit()
        print(msg)
        print('email sent')
    
    except Exception as ex:
        print(ex)

@app.route('/notify_me',methods=['GET','POST'])
def notify_me():
    pid=request.form.get('pid')
    pn=request.form.get('pn')
    pp=request.form.get('pp')
    pd=request.form.get('pd')
    pc=request.form.get('pc')
    ps=request.form.get('ps')
    pst=request.form.get('pst')
    pen=request.form.get('pen')
    nmsg='Product Details'+'\n'+pid+'\n'+pn+'\n'+pp+'\n'+pd+'\n'+pc+'\n'+ps+'\n'+pst+'\n'+pen
    print(nmsg)
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select email from user where username='"+ session['username'] +"'"
            cursor.execute(qstring)
            record=cursor.fetchall()
            uema=str(record[0][0])
            cursor.execute("""insert into un values(%s,%s)""",(session['username'],pid,))
            con.commit()
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    s_mail('Notification',nmsg,uema)
    myclient=pymongo.MongoClient('mongodb://localhost:27017/')
    mydb=myclient["oas"]
    mycol=mydb["notify"]
    mydict={'username':session['username'],'pid':str(pid)}
    mycol.insert(mydict)
    print('inserted')
    myclient.close()
    return get_prof()#render_template('Homepage.html')

@app.route('/hanrev',methods=['GET','POST'])
def handle_rev():
    disppr=request.form.get('pid')
    disppr=str(disppr)
    print('required--'+disppr)
    try :
        myclient=pymongo.MongoClient('mongodb://localhost:27017/')
        mydb=myclient["oas"]
        mycol=mydb["review"]
        el={"pid":str(request.form.get('pid')),"rno":str(request.form.get('rno')),"rval":str(request.form.get('rval'))}
        print(el)
        x=mycol.find(el)
        flag=0
        for eleme in x:
            print(eleme)
            flag=1
        if flag==1:
            el={"pid":str(request.form.get('pid'))}
            mycol.update(el,{"$set":{"rno":str(request.form.get('rno')),"rval":str(request.form.get('rval'))}})
            print('successful update')
        else:
            mycol.insert(el)
            print('successful insert')
    except Exception as Er:
        print(Er)
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
          #  qstring="update product set rnot=1 where prodid='"+ disppr +"'"
          #  cursor.execute(qstring)
            con.commit()
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    return render_template('Homepage.html')

@app.route("/blockchain",methods=["GET","POST"])
def blockchain():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)

    return render_template("blockchain.html",blockchain=blockchain,posts=posts)
@app.route('/timeline',methods=['POST','GET'])
def timeline():
    try:
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            cursor=con.cursor()
            cursor.execute("""select stdate,endate from lists where stdate > %s or endate > %s order by stdate""",(datetime.datetime.now(),datetime.datetime.now()))
            dts=cursor.fetchall()
            return render_template("timeline.html",dts=dts)
    except Error as Er:
        print(Er)
    return render_template("Homepage.html")

if __name__ == "__main__":
    socketio.run(app,debug=True)
    # app.run(debug=True)
    
        



