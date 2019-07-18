from threading import Thread
import pymongo


# 存储到Mongodb中
class Store(Thread):
    def __init__(self, url_queue, product_queue, *args, **kwargs):
        super(Store, self).__init__(*args, **kwargs)
        self.url_queue = url_queue
        self.product_queue = product_queue

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
        client = pymongo.MongoClient("127.0.0.1", port=27017)
        # 定义数据库名称为：JingDong_Products
        db = client.JingDong_Products
        # 定义数据集合的名称为：。。。
        collections = db.camera

        return collections
