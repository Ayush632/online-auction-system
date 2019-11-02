from flask import Flask,render_template,request,make_response,send_from_directory,session
import mysql.connector
from mysql.connector import Error
import threading
import datetime
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
# set FLASK_APP=main.py
# python -m flask run

UPLOAD_FOLDER = """C:\DBMS Project\static"""
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

CONNECTED_NODE_ADDRESS = "http://0.0.0.0:5002"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


uname='root'
pswd='leviton66'


def comp_auct(msg):
    print('comp auct called : received msg ' + msg)
    msg=str(msg)
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from bids where amt in (select max(amt) from bids where prodid='"+msg+"')"
            cursor.execute(qstring)
            record=cursor.fetchall()
            print(record[0])
            qstring="select username from lists1 where prodid='"+msg+"'"
            cursor.execute(qstring)
            sel=(cursor.fetchall())[0][0]
            sel=str(sel)
            qstring="update wallet set credits=credits-"+str(record[0][3])+" where username='"+str(record[0][0])+"'"
            cursor.execute(qstring)
            qstring="update wallet set credits=credits+"+str(record[0][3])+" where username='"+sel+"'"
            cursor.execute(qstring)
            qstring="""insert into purchases1 values(%s,%s)"""
            cursor.execute(qstring,(str(record[0][0]),msg))
            qstring="""insert into purchases2 values(%s,%s,%s)"""
            cursor.execute(qstring,(msg,str(record[0][2]),str(record[0][3])))
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
        'Buyer':last[2],
        'Seller':seller[0],
        'Productid':last[3],
        'price':cre[0],
        }
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
    requests.post(new_tx_address,json=post_object,headers={'Content-type': 'application/json'})
    response=requests.get("{}/mine".format(CONNECTED_NODE_ADDRESS))

def ch():
    curt=str(datetime.datetime.now())[:19]
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select * from lists2 where endate > '"+curt+"'"
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
                resp =make_response( render_template('homepage.html'))
                session['username']=username
                return resp
            else:
                return render_template('login.html')
    except Error as Er:
        print(Er)

def chkdat(stdat,endat):
    tbr=True
    con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
    if con.is_connected():
        print('connected')
        cursor=con.cursor()
        qstring="select * from lists2 where '"+stdat+"' between stdate and endate"
        cursor.execute(qstring)
        record=cursor.fetchall()
        if record!=[]:
            tbr=False
        qstring="select * from lists2 where '"+endat+"' between stdate and endate"
        cursor.execute(qstring)
        record=cursor.fetchall()
        if record!=[]:
            tbr=False
        cursor.close()
        con.close()
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
            print('uuuuuunnnnnn'+un)
            if len(record)!=0:
                qstring="insert into credpass (username,amt) values ('"+un+"','"+amt+"')"
                cursor.execute(qstring)   
                con.commit()
            else:
                wuser=''
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    if wuser=='':
        return render_template('wallet.html',ermsg='Couldnt find User')
    else:
        return render_template('wallet.html')

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
            un=record[0]
            # qstring="select * from wallet where username='"+wuser+"';"
            cursor.execute("""select * from wallet where username=%s """,(wuser,))
            record1=cursor.fetchall()
            cr=int(str(record1[0][1]))
            if len(record)!=0:
                otherv=str(cr+int(record[0][2]))
                # qstring="update wallet set credits = "+str(cr+int(str(un[2])))+"where username= '"+str(un[0])+"'"
                cursor.execute("""update wallet set credits = %s where username=%s""",(otherv,record[0][0],))   
                con.commit()
            else:
                wuser=''
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    if wuser=='':
        return render_template('wallet.html',ermsg='Enter Valid Passcode')
    else:
        return render_template('wallet.html')
                  
@app.route('/cur_auction',methods=['POST','GET'])
def cur_auction():
    curt=str(datetime.datetime.now())[:19]
    print('curt:'+curt+'|')
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="select prodname,prodprice,proddes,category,pimg,product.prodid,endate from product,lists2 where product.prodid=lists2.prodid and '"+curt+"' between lists2.stdate and lists2.endate"
            cursor.execute(qstring)
            record=cursor.fetchall()
            if record==[]:
                print('base')
                cursor.close()
                con.close()
                return render_template('nocurrauct.html')
            qstring="select amt,username from bids where prodid = '"+str(record[0][5])+"' order by amt"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            cursor.close()
            con.close()
            print(record)
            print('notbase')
            te=str(record[0][6])
            endtime=te[0:4]+","+str(int(te[5:7])-1)+","+te[8:10]+","+te[11:13]+","+te[14:16]+","+te[17:19]+",00"
            print('eeee'+endtime+'eeee')
            return render_template('currentauction.html',proname=record[0][0],proprice=record[0][1],prodes=record[0][2],procat=record[0][3],proimg=record[0][4],proid=record[0][5],initial=record1,endtimes=endtime)
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
    session.pop('username',none)
    return resp

@app.route('/enlist',methods=['POST','GET'])
def enlist():
    curt=str(datetime.datetime.now())[:19]
    print('curt:'+curt+'|')
    pname=request.form.get('pname')
    pprice=request.form.get('pprice')
    pdes=request.form.get('pdes')
    pst=request.form.get('stdat')+' '+request.form.get('sttim')+':00'
    # pen=request.form.get('endat')+' '+request.form.get('entim')+":00"
    pen='2019-11-06 14:30:00'
    print('pst-----'+pst+'pen-----'+pen)
    pcat=request.form.get('pcat')
    us=str(session['username'])
    if 'file' not in request.files:
        print('No file part')
    file = request.files.getlist('file')
    myclient=pymongo.MongoClient('mongodb://localhost:27017/')
    mydb=myclient["oas"]
    mycol=mydb["imgf"]
    fnames=[]
    for f in file:
        filenam = secure_filename(f.filename)
        print('file'+filenam)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filenam))
        fnames.append(filenam)
    mydict={'pid':str(pname[0]+pst),'iarr':fnames}
    mycol.insert(mydict)
    myclient.close()
    # for f in file:

        # if user does not select file, browser also
        # submit an empty part without filename
    # if file.filename == '':
    #     print('No selected file')
    # if file and allowed_file(file.filename):
    if chkdat(pst,pen)==False:
        return render_template('enlistproduct.html',ermsg='Try for different time slot')
    try :
        con=mysql.connector.connect(host='localhost',database='oas',user=uname,password=pswd)
        if con.is_connected():
            print('connected')
            cursor=con.cursor()
            qstring="""insert into product values(%s,%s,%s,%s,%s,%s,0)"""
            cursor.execute(qstring,(pname[0]+pst,pname,pprice,pdes,pcat,'rst'))
            qstring="""insert into lists1 values(%s,%s)"""
            cursor.execute(qstring,(us,pname[0]+pst))
            qstring="""insert into lists2 values(%s,%s,%s)"""
            cursor.execute(qstring,(pname[0]+pst,pst,pen))
            con.commit()
            qstring="""insert into bids values(%s,%s,%s,%s)"""
            cursor.execute(qstring,(session['username'],pname[0]+pst,curt,pprice))
            curt=datetime.datetime.now()
            uct=datetime.datetime(int(pen[:4]),int(pen[5:7]),int(pen[8:10]),int(pen[11:13]),int(pen[14:16]),int(pen[17:19]))
            threading.Timer((uct-curt).total_seconds(),comp_auct,args=[str(pname[0]+pst)]).start()
            print('started '+pname[0]+pst+' time '+str((uct-curt).total_seconds()))
            con.commit()
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)

    return render_template('enlistproduct.html')
#2019-12-10 09:30:00
#0123456789012345678
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
            qstring="select product.prodid,prodname,category,prodprice from lists1,product where lists1.prodid=product.prodid and username='"+uprof+"';"
            cursor.execute(qstring)
            rec=cursor.fetchall()
            qstring="select purchases1.prodid,prodname,category,prodprice,amount,rnot from purchases1,product,purchases2 where purchases1.prodid=product.prodid and purchases2.prodid=purchases1.prodid and username='"+uprof+"';"
            cursor.execute(qstring)
            rec2=cursor.fetchall()
            qstring="select prodid from lists1 where username='"+uprof+"';"
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
    

@app.route('/home')
def home_pg():
    return render_template('homepage.html')

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
            qstring="select prodid from lists2 where '"+curt+"' between lists2.stdate and lists2.endate"
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
                    emit('not enough','not enough',namespace='/')
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
            qstring="select username from lists1 where prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            sid=record1[0][0]
            qstring="select stdate,endate from lists2 where prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            std=record1[0][0]
            end=record1[0][1]
            qstring="select username,amount from purchases1,purchases2 where purchases1.prodid=purchases2.prodid and purchases1.prodid='"+ disppr +"'"
            cursor.execute(qstring)
            record1=cursor.fetchall()
            if(len(record)==0):
                buy='N/A'
                buyc='N/A'
            else:
                buy=str(record1[0][0])
                buyc=str(record1[0][1])
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
        
    return render_template('prodpage.html',rec=record[0],sid=sid,std=std,end=end,buy=buy,buyc=buyc)

@app.route('/review',methods=['GET','POST'])
def give_rev():
    return render_template('rev.html',pid=str(request.form.get('pid')))

@app.route('/home',methods=['GET','POST'])
def handle_rev():
    disppr=request.form.get('pid')
    disppr=str(disppr)
    print('required--'+disppr)
    try :
        myclient=pymongo.MongoClient('mongodb://localhost:27017/')
        mydb=myclient["oas"]
        mycol=mydb["review"]
        el={"pid":str(request.form.get('pid')),"rno":str(request.form.get('rno')),"rval":str(request.form.get('rval'))}
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
            qstring="update product set rnot=1 where prodid='"+ disppr +"'"
            cursor.execute(qstring)
            con.commit()
            cursor.close()
            con.close()
    except Error as Er:
        print(Er)
    return render_template('homepage.html')

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

if __name__ == "__main__":
    socketio.run(app,debug=True)
    # app.run(debug=True)
    
        



