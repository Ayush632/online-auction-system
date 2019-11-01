from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
class sol:
    def __init__(self):
        pass
    def myfun(self):
        client = MongoClient("127.0.0.1:27017")
        mydb=client['prj']
        mycol=mydb["notific"]
        mydoc=mycol.find({"prodid":2})
        
        for i in mydoc:
            print(type(i["mail"][0]))
            print(i["mail"][0])

p1=sol()
p1.myfun()
print("execute")