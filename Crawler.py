import threading
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from queue import Queue
import time
from Store import Store
from Settings import Settings
from Queuetolist import Queuetolist


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/63.0.3239.132 Safari/537.36'
}
data = {
    'cat': Settings.CAT
}
base_url = 'https://list.jd.com/list.html'


# 请求商品索引页
def get_index_page(index):
    page = index
    data['page'] = str(page)
    try:
        response = requests.get(url=base_url, headers=headers, params=data)
        if response.status_code == 200:
            index_html = response.text
            return parse_index_page(index_html)
        else:
            return None
    except RequestException:
        print('请求索引页失败！')


# 解析商品索引页，得到一页商品的商品详情url
def parse_index_page(html):
    soup = BeautifulSoup(html, 'lxml')
    lis = soup.find_all('li', class_="gl-item")
    for li in lis:
        url_content = li.find_all('div', class_="p-img")[0]
        url_content = str(url_content)
        part_url = re.search('<a href="(.*?)" target="_blank">', url_content, re.S).group(1)
        product_url = urljoin('https:', part_url)
        yield product_url


class Crawler(threading.Thread):

    def __init__(self, url_queue, product_queue):
        super(Crawler, self).__init__()
        # 商品的url队列
        self.url_queue = url_queue
        # 商品的详情队列
        self.product_queue = product_queue

    def run(self):
        while True:
            # 当商品url队列为空时，没有需解析的商品，退出循环
            if self.url_queue.empty():
                break
            # 调用解析商品的函数
            self.parse_product_page()

    # 请求商品详情页
    def get_product_page(self, url):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except RequestException:
            print('请求商品页失败！')

    # 解析商品详情页
    def parse_product_page(self):
        product_url = self.url_queue.get()
        sku = re.search(r'\d+', product_url).group(0)
        html = self.get_product_page(product_url)
        if html:
            soup = BeautifulSoup(html, 'lxml')
            div = soup.find('div', class_="p-parameter")
            image_div = soup.find('div', class_="spec-items")
            if div:
                lis = div.find_all('li')
                product = {}
                images = []
                for li in lis:
                    content = li.get_text().strip().split('：')
                    product[content[0]] = content[1]
                image_lis = image_div.find_all('img')
                for li in image_lis:
                    image = 'https:' + li["src"]
                    images.append(image)
                product['图像'] = images
                price = self.get_price(sku)
                product['价格'] = price
                self.product_queue.put(product)
                print('成功抓取商品', product_url)

    # 获取商品价格
    def get_price(self, sku):
        price_base_url = 'https://c.3.cn/recommend'
        price_url_data = {
            'callback': 'handleComboCallback',
            'methods': 'accessories',
            'p': '103003',
            'sku': sku,
            'cat': '670,671,1105'
        }
        try:
            s = requests.Session()
            # 重试次数为3
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))
            # 超时时间为5s
            response = s.get(url=price_base_url, headers=headers, params=price_url_data, timeout=5)
            if response.status_code == 200:
                try:
                    price = re.findall(r'"wMaprice":(\d+.\d+)', response.text, re.S)[-1]
                    return price
                except IndexError:
                    price = 0
                    return price
            else:
                return None
        except RequestException:
            print('商品id：'+sku+'价格获取失败！')


def main():
    url_queue = Queue()
    product_queue = Queue()
    # 线程队列
    thread_list1 = []
    thread_list2 = []
    index = Settings.INDEX + 1
    # 获取前INDEX页商品的所有url，放入url队列中
    for i in range(1, index):
        for x in [url for url in get_index_page(i)]:
            if x:
                print('获取到：', x)
                url_queue.put(x)
        print('#'*30)
    print('所有商品url获取完毕')
    # 多线程解析
    for x in range(10):
        c = Crawler(url_queue, product_queue)
        c.start()
        thread_list1.append(c)
    for i in thread_list1:
        i.join()
    print('开始存储。。。。。。')
    # 多线程存储
    # for x in range(10):
    #     s = Store(url_queue, product_queue)
    #     s.start()
    #     thread_list2.append(s)
    # for i in thread_list2:
    #     i.join()
    for x in range(10):
        s = Queuetolist(url_queue, product_queue)
        s.start()
        thread_list2.append(s)
    for i in thread_list2:
        i.join()


if __name__ == '__main__':
    # 计算耗时
    start = time.time()
    main()
    print('[info]耗时：%s' % (time.time() - start))
