import pymongo
from Settings import Settings


# 存储到Mongodb中
# 此类是将数据从队列中取出全部存入一个空列表List中，再通过insert_many一次性存入数据库中
class Stored:
    def __init__(self, pro_list):
        self.mongo_uri = Settings.MONGO_URI
        self.mongo_db = Settings.MONGO_DB
        self.mongo_collections = Settings.MONGO_COLLECTIONS
        self.pro_list = pro_list

    def run(self):
        self.save_in_db(self.pro_list)
        print('Done!')

    def save_in_db(self, product):
        collections = self.connect_db()
        try:
            collections.insert_many(product, ordered=False)
        except Exception:
            print('Done!')

    def connect_db(self):
        client = pymongo.MongoClient(self.mongo_uri)
        db = client[self.mongo_db]
        collections = db[self.mongo_collections]
        return collections
