from threading import Thread
import pymongo
from Settings import Settings


# 存储到Mongodb中
class Store(Thread):
    def __init__(self, url_queue, product_queue):
        super(Store, self).__init__()
        self.url_queue = url_queue
        self.product_queue = product_queue
        self.mongo_uri = Settings.MONGO_URI
        self.mongo_db = Settings.MONGO_DB
        self.mongo_collections = Settings.MONGO_COLLECTIONS

    def run(self):
        while True:
            if self.url_queue.empty() and self.product_queue.empty():
                break
            product = self.product_queue.get()
            self.save_in_db(product)
            print('成功写入数据库：', product['商品编号'])

    def save_in_db(self, product):
        collections = self.connect_db()
        collections.insert_one(product)

    def connect_db(self):
        client = pymongo.MongoClient(self.mongo_uri)
        db = client[self.mongo_db]
        collections = db[self.mongo_collections]
        return collections
