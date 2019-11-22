import threading
import datetime

def comp_auct(msg):
    print(msg)
    print('done')

curt=datetime.datetime.now()
pen='2019-10-29 16:36:00'
uct=datetime.datetime(int(pen[:4]),int(pen[5:7]),int(pen[8:10]),int(pen[11:13]),int(pen[14:16]),int(pen[17:19]))
times=(uct-curt).total_seconds()
threading.Timer(times,comp_auct,args=['hey']).start()
print('started '+' time '+str(times))