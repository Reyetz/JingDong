import threading
from Storage import Stored


# 将数据从队列中存到列表List中
class Queuetolist(threading.Thread):
    def __init__(self, url_queue, product_queue):
        super(Queuetolist, self).__init__()
        self.url_queue = url_queue
        self.product_queue = product_queue
        self.pro_list = []
        self.done_sign = 0

    def run(self):
        while True:
            if self.url_queue.empty() and self.product_queue.empty():
                stored = Stored(self.pro_list)
                stored.run()
                break
            product = self.product_queue.get()
            self.pro_list.append(product)
            print('成功加入商品列表：', product['商品编号'])
