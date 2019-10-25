# JingDong
（爬取京东商城的指定类型产品的所有上架商品的信息）
### 配置Setting.py

例：
```
CAT = '670,671,672'
INDEX = 10
MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_DB = 'JingDong_Products'
MONGO_COLLECTIONS = 'laptops'
```
(可在商城主页中点击所要获取的商品的类别，然后可在URL上看到对应的CAT值)\
例：\
商品冰箱：https://list.jd.com/list.html?cat=737,794,878\
对应的CAT值为：737,794,878

### 运行Crawler.py
（本项目为个人学习项目，感兴趣的朋友可以star噢，可相互交流学习，谢谢）
