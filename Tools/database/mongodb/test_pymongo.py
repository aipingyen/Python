from pymongo import MongoClient
client = MongoClient("mongodb://root:root@192.168.1.208:27017/admin")
db = client['test']
collection = db['user']

# collection.remove()
# collection.insert({"name":"wild hunt"})

result = collection.find()
for r in result:
    print(r)
