# -*- coding: utf-8 -*-
"""Crawler experiments: Qunar tours/trains, Ctrip hotels/flights/attractions.

Generated from: crap.ipynb
Notebook outputs are intentionally omitted; only source code cells are kept.
"""

# %% [notebook cell 1]
import requests

all_pages_data = []  # 存储所有页面的数据

for i in range(1, 3):  # 爬取第1页和第2页
    url = f'https://piao.qunar.com/daytrip/list.htm?region=%E9%BB%94%E5%8D%97&from=mpldaytrip_guoneihot&page={i}'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.9 Safari/537.36"
    }
    res = requests.get(url, headers=headers).text
    all_pages_data.append(res)  # 添加到列表

# 打印所有页面的数据（测试）
for idx, page_data in enumerate(all_pages_data, 1):
    print(f"第 {idx} 页数据长度：{len(page_data)}")

# %% [notebook cell 2]
from pyquery import PyQuery as pq
# 数据初始化
doc = pq("".join(all_pages_data))

# %% [notebook cell 3]
# 通过类选择器获取旅游项目，项目价格以及评分信息
name =doc(".name")
sight_item_price=doc(".sight_item_parice")
relation_count=doc(".relation_count")
print(name.text())
sight_item_price

# %% [notebook cell 4]
 # 通过类选择器获取旅游项目，项目价格以及评分信息
name = list(doc(".name").items())  # 转为列表
sight_item_price = list(doc(".sight_item_price").items())
relation_count = list(doc(".relation_count").items())

# %% [notebook cell 5]
all_travels = []  # 创建一个空列表收集结果

for x,s,f in zip(name,sight_item_price,relation_count):
    name1 = x.text()
    sight_item_price1 = s.text()
    relation_count1 = f.text()
    travel = name1 + sight_item_price1 + relation_count1
    all_travels.append(travel)  # 添加到列表

# 循环结束后打印所有结果
for item in all_travels:
    print(item)
# 或者直接打印整个列表
print(all_travels)

# %% [notebook cell 6]
all_travels

# %% [notebook cell 7]
# 确保 all_travels 有数据
print("待写入的数据：", all_travels)  # 调试用

# 使用 with 自动管理文件
with open("广州一日游1.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_travels) + "\n")  # 每个条目占一行

print("文件写入完成！")

# %% [notebook cell 8]
import requests
from pyquery import PyQuery as pq
import time
import csv
from datetime import datetime

def scrape_qunar_tours():
    # 1. 爬取多页数据
    all_pages_data = []
    for i in range(1, 5):  # 爬取第1页和第2页
        url = f'https://piao.qunar.com/daytrip/list.htm?region=%E9%BB%94%E5%8D%97&from=mpldaytrip_guoneihot&page={i}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            all_pages_data.append(response.text)
            print(f"成功获取第 {i} 页数据")
            time.sleep(1)
        except Exception as e:
            print(f"获取第 {i} 页数据失败: {e}")
    
    # 2. 解析数据
    all_travels = []
    for page_html in all_pages_data:
        doc = pq(page_html)
        
        names = list(doc(".name").items())
        prices = list(doc(".sight_item_price").items())
        ratings = list(doc(".relation_count").items())
        
        min_length = min(len(names), len(prices), len(ratings))
        for i in range(min_length):
            all_travels.append({
                "项目名称": names[i].text().strip(),
                "价格": prices[i].text().strip(),
                "评分": ratings[i].text().strip(),
                "抓取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # 3. 存储为CSV
    if all_travels:
        filename = f"贵州一日游_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig解决Excel中文乱码
            writer = csv.DictWriter(f, fieldnames=["项目名称", "价格", "评分", "抓取时间"])
            writer.writeheader()
            writer.writerows(all_travels)
        print(f"成功保存 {len(all_travels)} 条数据到 {filename}")
    else:
        print("未获取到有效数据")

if __name__ == "__main__":
    scrape_qunar_tours()

# %% [notebook cell 9]
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyquery import PyQuery as pq
import csv
import time

def scrape_train_tickets():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    url = "https://train.qunar.com/stationToStation.htm?fromStation=上海&toStation=贵阳&date=2025-06-5"
    driver.get(url)
    time.sleep(3)  # 关键：等待动态加载
    html = driver.page_source
    driver.quit()

    doc = pq(html)
    trains = []
    for item in doc('li[data-testdt]').items():
        train = {
            "车次": item.find('.js-trainNum').text().strip(),
            "出发站": item.find('.start span').eq(0).text().strip(),
            "到达站": item.find('.end span').eq(0).text().strip(),
            "出发时间": item.find('.startime').text().strip(),
            "到达时间": item.find('.endtime').text().strip(),
            "历时": item.find('.duration').text().strip(),
            "硬座价格": item.find('.ticketed:contains("硬座") .price').text().strip() or "无",
            "硬卧价格": item.find('.ticketed:contains("硬卧") .price').text().strip() or "无",
            "软卧价格": item.find('.ticketed:contains("软卧") .price').text().strip() or "无",
            "无座价格": item.find('.ticketed:contains("无座") .price').text().strip() or "无",
            "硬座余票": item.find('.surplus span').eq(0).text().strip() or "无",
            "硬卧余票": item.find('.surplus span').eq(1).text().strip() or "无",
            "软卧余票": item.find('.surplus span').eq(2).text().strip() or "无",
            "无座余票": item.find('.surplus span').eq(3).text().strip() or "无",
            "二等座价格": item.find('.ticketed:contains("二等座") .price').text().strip() or "无",
            "一等座价格": item.find('.ticketed:contains("一等座") .price').text().strip() or "无",
            "商务座价格": item.find('.ticketed:contains("商务座") .price').text().strip() or "无",
            "商务座余票": item.find('.surplus span').eq(0).text().strip() or "无",
            "一等座余票": item.find('.surplus span').eq(1).text().strip() or "无",
            "二等座余票": item.find('.surplus span').eq(2).text().strip() or "无"

        }
        trains.append(train)

    if trains:
        with open("train_tickets.csv", "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=trains[0].keys())
            writer.writeheader()
            writer.writerows(trains)
        print(f"成功保存 {len(trains)} 条数据")
    else:
        print("未找到车次信息（检查页面结构或尝试手动访问URL）")

if __name__ == "__main__":
    scrape_train_tickets()

# %% [notebook cell 10]
import requests
import json
import pprint

headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://hotels.ctrip.com",
    "p": "<fill-in-locally>",
    "phantom-token": "<fill-in-locally>",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://hotels.ctrip.com/",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Microsoft Edge\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
}
cookies = {}  # Fill with valid cookies locally if this endpoint requires authentication.
url = "https://m.ctrip.com/restapi/soa2/31454/json/fetchHotelList"

# Initialize an empty list to store all hotel data
all_hotel_data = []

# Loop from pageIndex 1 to 40
for page_number in range(1, 8): # range(1, 41) will generate numbers from 1 to 40
    data = {
    "hotelIdFilter": {
        "hotelAldyShown": []
    },
    "destination": {
        "type": 1,
        "geo": {
            "cityId": -1,
            "provinceId": 26,
            "countryId": 1
        },
        "keyword": {
            "word": ""
        }
    },
    "date": {
        "dateType": 1,
        "dateInfo": {
            "checkInDate": "20250602",
            "checkOutDate": "20250605"
        }
    },
    "filters": [
        {
            "filterId": "29|1",
            "type": "29",
            "value": "1|1",
            "subType": "2"
        }
    ],
    "extraFilter": {
        "childInfoItems": [],
        "sessionId": ""
    },
    "paging": {
        "pageCode": "102002",
        "pageIndex": 1,
        "pageSize": 10
    },
    "roomQuantity": 1,
    "recommend": {
        "nearbyHotHotel": {}
    },
    "genk": True,
    "residenceCode": "CN",
    "head": {
        "platform": "PC",
        "cid": "09031100314493817182",
        "cver": "hotels",
        "bu": "HBU",
        "group": "ctrip",
        "aid": "4897",
        "sid": "",
        "ouid": "",
        "locale": "zh-CN",
        "timezone": "8",
        "currency": "CNY",
        "pageId": "102002",
        "vid": "1748248815616.5bf36zn2y892",
        "guid": "09031100314493817182",
        "isSSR": False
    },
    "ServerData": ""
}

    # Convert the data dictionary to a JSON string
    data_json = json.dumps(data, separators=(',', ':'))

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, cookies=cookies, data=data_json).json()

        # Extract hotel list for the current page
        current_page_hotel_list = response['data']['hotelList']

        # Extend the all_hotel_data list with the current page's hotel list
        all_hotel_data.extend(current_page_hotel_list)

        print(f"Successfully fetched page {page_number}")

    except Exception as e:
        print(f"An error occurred while fetching page {page_number}: {e}")

# After the loop, all_hotel_data will contain data from all pages
print("\n--- All Collected Hotel Data ---")
pprint.pprint(all_hotel_data)
print(f"\nTotal hotels collected: {len(all_hotel_data)}")

# %% [notebook cell 11]
import requests
import json
import pprint

headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://hotels.ctrip.com",
    "p": "<fill-in-locally>",
    "phantom-token": "<fill-in-locally>",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://hotels.ctrip.com/",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Microsoft Edge\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
}
cookies = {}  # Fill with valid cookies locally if this endpoint requires authentication.
url = "https://m.ctrip.com/restapi/soa2/31454/json/fetchHotelList"

# Initialize an empty list to store all hotel data
all_hotel_data = []

# Loop from pageIndex 1 to 80
for page_number in range(1, 100): # range(1, 41) will generate numbers from 1 to 40
    data = {
    "hotelIdFilter": {
        "hotelAldyShown": []
    },
    "destination": {
        "type": 1,
        "geo": {
            "cityId": -1,
            "provinceId": 26,
            "countryId": 1
        },
        "keyword": {
            "word": ""
        }
    },
    "date": {
        "dateType": 1,
        "dateInfo": {
            "checkInDate": "20250602",
            "checkOutDate": "20250603"
        }
    },
    "filters": [
        {
            "filterId": "29|1",
            "type": "29",
            "value": "1|1",
            "subType": "2"
        }
    ],
    "extraFilter": {
        "childInfoItems": [],
        "sessionId": ""
    },
    "paging": {
        "pageCode": "102002",
        "pageIndex": 1,
        "pageSize": 20
    },
    "roomQuantity": 1,
    "recommend": {
        "nearbyHotHotel": {}
    },
    "genk": True,
    "residenceCode": "CN",
    "head": {
        "platform": "PC",
        "cid": "09031100314493817182",
        "cver": "hotels",
        "bu": "HBU",
        "group": "ctrip",
        "aid": "",
        "sid": "",
        "ouid": "",
        "locale": "zh-CN",
        "timezone": "8",
        "currency": "CNY",
        "pageId": "102002",
        "vid": "1748248815616.5bf36zn2y892",
        "guid": "09031100314493817182",
        "isSSR": False
    },
    "ServerData": ""
}
    # Convert the data dictionary to a JSON string
    data_json = json.dumps(data, separators=(',', ':'))

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, cookies=cookies, data=data_json).json()

        # Extract hotel list for the current page
        current_page_hotel_list = response['data']['hotelList']

        # Extend the all_hotel_data list with the current page's hotel list
        all_hotel_data.extend(current_page_hotel_list)

        print(f"Successfully fetched page {page_number}")

    except Exception as e:
        print(f"An error occurred while fetching page {page_number}: {e}")

# After the loop, all_hotel_data will contain data from all pages
print("\n--- All Collected Hotel Data ---")
pprint.pprint(all_hotel_data)
print(f"\nTotal hotels collected: {len(all_hotel_data)}")

# %% [notebook cell 12]
import pandas as pd

lis = []  # Used to store information for each hotel

# Assuming 'all_hotel_data' contains the aggregated data from the previous script
# If you're running this as a separate script, you'll need to ensure 'all_hotel_data' is defined
# and populated with the data you fetched across all pages.
# For example, if you ran the previous code, all_hotel_data would be available.

for item in all_hotel_data:  # Iterate through the combined list of all hotel data
    name = item["hotelInfo"]["nameInfo"]["name"]
    address = item["hotelInfo"]["positionInfo"]["address"]
    position_detail = item["hotelInfo"]["positionInfo"]["positionDesc"]
    
    # Handle cases where 'roomInfo' might be empty or missing 'priceInfo'
    price = item["roomInfo"][0]["priceInfo"]["price"] if item.get("roomInfo") and item["roomInfo"] and item["roomInfo"][0].get("priceInfo") else None
    room_intro = item["roomInfo"][0]["summary"]["physicsName"] if item.get("roomInfo") and item["roomInfo"] and item["roomInfo"][0].get("summary") else None
    
    judge = item["hotelInfo"]["commentInfo"]["commentDescription"]
    score = item["hotelInfo"]["commentInfo"]["commentScore"]
    
    # Process 'commenterNumber' to extract pure numerical content
    comment = ''.join(item["hotelInfo"]["commentInfo"]["commenterNumber"]).replace('条点评','')
    
    # --- FIX START ---
    # Handle cases where 'oneSentenceComment' might be missing or empty
    tag_info = None # Default value
    if item["hotelInfo"]["commentInfo"].get("oneSentenceComment") and \
       len(item["hotelInfo"]["commentInfo"]["oneSentenceComment"]) > 0 and \
       item["hotelInfo"]["commentInfo"]["oneSentenceComment"][0].get("tagTitle"):
        tag_info = ''.join(item["hotelInfo"]["commentInfo"]["oneSentenceComment"][0]["tagTitle"]).replace('"','')
    # --- FIX END ---
    
    # Handle cases where 'multiImgs' might be empty
    room_img = item["hotelInfo"]["hotelImages"]["multiImgs"][0]["url"] if item["hotelInfo"]["hotelImages"].get("multiImgs") else None
    
    # Print for verification (optional)
    print(name, address, position_detail, price, room_intro, judge, score, comment, tag_info, room_img)
    
    dit = {
        '酒店名称': name,
        '酒店价格': price,
        '酒店地址': address,
        '酒店位置': position_detail,
        '酒店简介': room_intro,
        '酒店评价': judge,
        '酒店评分': score,
        '酒店评论数': comment,
        '酒店标签': tag_info,
        '酒店图片': room_img
    }
    lis.append(dit)

# After the loop finishes, convert the list of dictionaries to a DataFrame and save to CSV
df = pd.DataFrame(lis)
df.to_csv('hotel_贵州.csv', index=False, encoding='utf-8-sig')

print("\n--- All hotel information has been saved to hotel_NC.csv ---")

# %% [notebook cell 13]
#导包
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line,Bar
 
df = pd.read_csv('hotel_贵州.csv', encoding='utf-8-sig')  # 读取数据文件
# 创建一个柱状图对象
bar = (
    Bar()
    .add_xaxis(df['酒店名称'].tolist())
    # 只显示 数值的最大值与最小值
    .add_yaxis("酒店价格", df['酒店价格'].tolist(),markpoint_opts=opts.MarkPointOpts(data=[
        opts.MarkPointItem(type_='max', name="最大值" ),
        opts.MarkPointItem(type_='min', name="最小值")
    ]))
    .add_yaxis("酒店评分", df['酒店评分'].tolist(),markpoint_opts=opts.MarkPointOpts(data=[
        opts.MarkPointItem(type_='max', name="最大值" ),
        opts.MarkPointItem(type_='min', name="最小值")
    ]))
    .add_yaxis("酒店评论数", df['酒店评论数'].tolist(),markpoint_opts=opts.MarkPointOpts(data=[
        opts.MarkPointItem(type_='max', name="最大值" ),
        opts.MarkPointItem(type_='min', name="最小值")
    ]))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="酒店信息柱状图"),
        xaxis_opts=opts.AxisOpts(name="酒店名称", axislabel_opts={"rotate": 45},is_show=False),
        yaxis_opts=opts.AxisOpts(name="数值"),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        legend_opts=opts.LegendOpts(pos_top="5%",is_show=True)
    )
    # 将每个柱状图的数据隐藏
    .set_series_opts(label_opts=opts.LegendOpts(is_show=False))
 
)
# 渲染图表并保存为 HTML 文件
bar.render("hotel_bar_chart_贵州.html")

# %% [notebook cell 14]
import magic
import io
import os
import gzip
import time
import json
import pandas as pd
from seleniumwire import webdriver
from datetime import datetime as dt, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import threading

# 爬取的城市
crawl_citys = ["上海",  "贵阳"]

# 爬取日期范围：起始日期。格式'2023-12-01'
begin_date = None

# 爬取日期范围：结束日期。格式'2023-12-31'
end_date = None

# 爬取T+N，即N天后
start_interval = 1

# 爬取的日期
crawl_days = 6

# 设置各城市爬取的时间间隔（单位：秒）
crawl_interval = 5

# 日期间隔
days_interval = 1

# 设置页面加载的最长等待时间（单位：秒）
max_wait_time = 10

# 最大错误重试次数
max_retry_time = 5

# 是否只抓取直飞信息（True: 只抓取直飞，False: 抓取所有航班）
direct_flight = True

# 是否抓取航班舒适信息（True: 抓取，False: 不抓取）
comft_flight = False

# 是否删除不重要的信息
del_info = False

# 是否重命名DataFrame的列名
rename_col = True

# 调试截图
enable_screenshot = False

# 允许登录（可能必须要登录才能获取数据）
login_allowed = True

# 账号
accounts = ['','']

# 密码
passwords = ['','']

#本地登录缓存
COOKIES_FILE = "cookies.json"
REQUIRED_COOKIES = ["AHeadUserInfo", "DUID", "IsNonUser", "_udl", "cticket", "login_type", "login_uid"]

def init_driver():
    # options = webdriver.ChromeOptions() # 创建一个配置对象
    options = webdriver.EdgeOptions()  # 创建一个配置对象
    options.add_argument("--incognito")  # 隐身模式（无痕模式）
    # options.add_argument('--headless')  # 启用无头模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--pageLoadStrategy=eager")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-certificate-errors-spki-list")
    options.add_argument("--ignore-ssl-errors")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 不显示正在受自动化软件控制的提示
    # 如果需要指定Chrome驱动的路径，取消下面这行的注释并设置正确的路径
    # chromedriver_path = '/path/to/chromedriver'
    # 如果需要指定路径，可以加上executable_path参数
    # driver = webdriver.Chrome(options=options)  
    driver = webdriver.Edge(options=options)
    driver.maximize_window()

    return driver

def gen_citys(crawl_citys):
    # 生成城市组合表
    citys = []
    ytic = list(reversed(crawl_citys))
    for m in crawl_citys:
        for n in ytic:
            if m == n:
                continue
            else:
                citys.append([m, n])
    return citys

def generate_flight_dates(n, begin_date, end_date, start_interval, days_interval):
    flight_dates = []
    
    if begin_date:
        begin_date = dt.strptime(begin_date, "%Y-%m-%d")
    elif start_interval:
        begin_date = dt.now() + timedelta(days=start_interval)
        
    for i in range(0, n, days_interval):
        flight_date = begin_date + timedelta(days=i)

        flight_dates.append(flight_date.strftime("%Y-%m-%d"))
    
    # 如果有结束日期，确保生成的日期不超过结束日期
    if end_date:
        end_date = dt.strptime(end_date, "%Y-%m-%d")
        flight_dates = [date for date in flight_dates if dt.strptime(date, "%Y-%m-%d") <= end_date]
        # 继续生成日期直到达到或超过结束日期
        while dt.strptime(flight_dates[-1], "%Y-%m-%d") < end_date:
            next_date = dt.strptime(flight_dates[-1], "%Y-%m-%d") + timedelta(days=days_interval)
            if next_date <= end_date:
                flight_dates.append(next_date.strftime("%Y-%m-%d"))
            else:
                break
    
    return flight_dates

# element_to_be_clickable 函数来替代 expected_conditions.element_to_be_clickable 或 expected_conditions.visibility_of_element_located
def element_to_be_clickable(element):
    def check_clickable(driver):
        try:
            if element.is_enabled() and element.is_displayed():
                return element  # 当条件满足时，返回元素本身
            else:
                return False
        except:
            return False

    return check_clickable

class DataFetcher(object):
    def __init__(self, driver):
        self.driver = driver
        self.date = None
        self.city = None
        self.err = 0  # 错误重试次数
        self.switch_acc = 0 #切换账户
        self.comfort_data = None  # 航班舒适度信息

    def refresh_driver(self):
        try:
            self.driver.refresh()
        except Exception as e:
            # 错误次数+1
            self.err += 1

            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} refresh_driver:刷新页面失败，错误类型：{type(e).__name__}, 详细错误信息：{str(e).split("Stacktrace:")[0]}'
            )
            
            # 保存错误截图
            if enable_screenshot:
                self.driver.save_screenshot(
                    f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                )
            if self.err < max_retry_time:
                # 刷新页面
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} refresh_driver：刷新页面')
                self.refresh_driver()

            # 判断错误次数
            if self.err >= max_retry_time:
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,refresh_driver:不继续重试'
                )
    
    def remove_btn(self):
        try:
            #WebDriverWait(self.driver, max_wait_time).until(lambda d: d.execute_script('return typeof jQuery !== "undefined"'))
            # 移除提醒
            self.driver.execute_script("document.querySelectorAll('.notice-box').forEach(element => element.remove());")
            # 移除在线客服
            self.driver.execute_script("document.querySelectorAll('.shortcut, .shortcut-link').forEach(element => element.remove());")
            # 移除分享链接
            self.driver.execute_script("document.querySelectorAll('.shareline').forEach(element => element.remove());")
            '''
            # 使用JavaScript删除有的<dl>标签
            self.driver.execute_script("""
                var elements = document.getElementsByTagName('dl');
                while(elements.length > 0){
                    elements[0].parentNode.removeChild(elements[0]);
                }
            """)
            '''
        except Exception as e:
            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} remove_btn:提醒移除失败，错误类型：{type(e).__name__}, 详细错误信息：{str(e).split("Stacktrace:")[0]}'
            )

    def check_verification_code(self):
        try:
            # 检查是否有验证码元素，如果有，则需要人工处理
            if (len(self.driver.find_elements(By.ID, "verification-code")) + len(self.driver.find_elements(By.CLASS_NAME, "alert-title"))):
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} check_verification_code：验证码被触发verification-code/alert-title，请手动完成验证。')
    
                user_input_completed = threading.Event()
                # 等待用户手动处理验证码
                def wait_for_input():
                    input("请完成验证码，然后按回车键继续...")
                    user_input_completed.set()
    
                input_thread = threading.Thread(target=wait_for_input)
                input_thread.start()
    
                # 设置手动验证超时时间
                timeout_seconds = crawl_interval * 100
    
                input_thread.join(timeout=timeout_seconds)
    
                if user_input_completed.is_set():
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} check_verification_code：验证码处理完成，继续执行。')
    
                    # 等待页面加载完成
                    WebDriverWait(self.driver, max_wait_time).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "pc_home-jipiao"))
                    )
                    
                    # 移除注意事项
                    self.remove_btn()
                    return True
                else:
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} check_verification_code: 手动验证超时 {timeout_seconds} 秒')
                    self.driver.quit()
                    self.driver = init_driver()
                    self.err = 0
                    self.switch_acc += 1
                    self.get_page(1)
                    return False
            else:
                # 移除注意事项
                self.remove_btn()
                # 如果没有找到验证码元素，则说明页面加载成功，没有触发验证码
                return True
        except Exception as e:
            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} check_verification_code:未知错误，错误类型：{type(e).__name__}, 详细错误信息：{str(e).split("Stacktrace:")[0]}'
            )
            return False

    def load_cookies(self, account):
        if os.path.exists(COOKIES_FILE):
            try:
                with open(COOKIES_FILE, "r") as f:
                    cookies_all = json.load(f)
                return cookies_all.get(account)
            except Exception as e:
                print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} load_cookies: 读取 cookies 出错：{e}")
                return None
        return None

    def save_cookies(self, account, cookies):
        cookies_all = {}
        if os.path.exists(COOKIES_FILE):
            try:
                with open(COOKIES_FILE, "r") as f:
                    cookies_all = json.load(f)
            except Exception:
                cookies_all = {}
        cookies_all[account] = cookies
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies_all, f)

    def delete_cookies(self, account):
        try:
            if os.path.exists(COOKIES_FILE):
                with open(COOKIES_FILE, "r") as f:
                    cookies_all = json.load(f)
                if account in cookies_all:
                    del cookies_all[account]
                    with open(COOKIES_FILE, "w") as f:
                        json.dump(cookies_all, f)
                    print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} login: 成功删除账号 {account} 的 cookies")
        except Exception as e:
            print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} login: 删除账号 {account} cookies 失败：{e}")

    def login(self):
        if login_allowed:
            
            account = accounts[self.switch_acc % len(accounts)]
            password = passwords[self.switch_acc % len(passwords)]
            
            # ===== 尝试使用本地缓存的 cookies 登录 =====
            local_cookies = self.load_cookies(account)
            if local_cookies:
                print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} login: 检测到本地 cookies，尝试通过 cookies 登录")
                for cookie in local_cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} login: 添加 cookie {cookie.get('name')} 失败：{e}")
                
                try:
                    # 检测登录状态，通过https://my.ctrip.com/myinfo/home
                    self.driver.get('https://my.ctrip.com/myinfo/home')
                    
                    WebDriverWait(self.driver, max_wait_time).until(
                        lambda d: d.current_url == 'https://my.ctrip.com/myinfo/home'
                    )
                    print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} login: 已通过 cookie 登录")
                    self.err += 99
                    return 1
                except Exception:
                    print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 错误次数【{self.err}-{max_retry_time}】 login: cookie 登录失效，重新走登录流程")
                    self.err += 1
                    if self.err >= max_retry_time:
                        print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} login: cookie 登录失败次数超过 {max_retry_time} 次，删除该账号 cookies")
                        self.delete_cookies(account)
                        self.err = 0
                    self.login()
            else:
                try:
                    if len(self.driver.find_elements(By.CLASS_NAME, "lg_loginbox_modal")) == 0:
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login:未弹出登录界面')
                        WebDriverWait(self.driver, max_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "tl_nfes_home_header_login_wrapper_siwkn")))
                        # 点击飞机图标，返回主界面
                        ele = WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(self.driver.find_element(By.CLASS_NAME, "tl_nfes_home_header_login_wrapper_siwkn")))
                        ele.click()
                        #等待页面加载
                        WebDriverWait(self.driver, max_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "lg_loginwrap")))
                    else:
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login:已经弹出登录界面')
                    
                    ele = WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(self.driver.find_elements(By.CLASS_NAME, "r_input.bbz-js-iconable-input")[0]))
                    ele.send_keys(account)
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login:输入账户成功')
                    
                    ele = WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(self.driver.find_element(By.CSS_SELECTOR, "div[data-testid='accountPanel'] input[data-testid='passwordInput']")))
                    ele.send_keys(password)
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login:输入密码成功')
                    
                    ele = WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(self.driver.find_element(By.CSS_SELECTOR, '[for="checkboxAgreementInput"]')))
                    ele.click()
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login:勾选同意成功')
                    
                    ele = WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(self.driver.find_elements(By.CLASS_NAME, "form_btn.form_btn--block")[0]))
                    ele.click()
    
                    # 检查是否出现验证码验证页面（max_wait_time秒内检测）
                    try:
                        WebDriverWait(self.driver, max_wait_time).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='doubleAuthSwitcherBox']"))
                        )
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: 检测到验证码验证页面')
                        
                        # 定义验证码弹窗的父级选择器
                        double_auth_selector = "[data-testid='doubleAuthSwitcherBox']"
                        
                        # 从 doubleAuthSwitcherBox 内定位发送验证码按钮并点击
                        send_btn = WebDriverWait(self.driver, max_wait_time).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f"{double_auth_selector} dl[data-testid='dynamicCodeInput'] a.btn-primary-s"))
                        )
                        send_btn.click()
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: 发送验证码按钮点击')
                        
                        # 使用线程等待用户在控制台输入验证码，超时则按超时处理逻辑
                        verification_code = [None]
                        user_input_completed = threading.Event()
                        
                        def wait_for_verification_input():
                            verification_code[0] = input("请输入收到的验证码: ")
                            user_input_completed.set()
                        
                        input_thread = threading.Thread(target=wait_for_verification_input)
                        input_thread.start()
                        timeout_seconds = crawl_interval * 100
                        input_thread.join(timeout=timeout_seconds)
                        
                        if not user_input_completed.is_set():
                            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: 验证码输入超时 {timeout_seconds} 秒')
                            self.switch_acc += 1
                            self.err += 99
                            return 0
                        
                        # 从 doubleAuthSwitcherBox 内定位验证码输入框，并输入验证码
                        code_input = WebDriverWait(self.driver, max_wait_time).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f"{double_auth_selector} input[data-testid='verifyCodeInput']"))
                        )
                        code_input.send_keys(verification_code)
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: 验证码输入成功')
                        
                        # 从 doubleAuthSwitcherBox 内定位并点击“验 证”按钮
                        verify_btn = WebDriverWait(self.driver, max_wait_time).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f"{double_auth_selector} dl[data-testid='dynamicVerifyButton'] input[type='submit']"))
                        )
                        verify_btn.click()
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: 验证码提交成功')
                        
                        # 等待验证码验证后的页面加载，比如首页的某个关键元素
                        WebDriverWait(self.driver, max_wait_time).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "pc_home-jipiao"))
                        )
                    except Exception as e:
                        # 如果max_wait_time秒内未检测到验证码页面，则认为是正常登录流程
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: 未检测到验证码验证页面，继续执行')
                    
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login：登录成功')
                    # 保存登录截图
                    if enable_screenshot:
                        self.driver.save_screenshot(
                            f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                        )
                    time.sleep(crawl_interval*3)
                    
                    # ===== 登录成功后提取需要的 cookies 并保存 =====
                    all_cookies = self.driver.get_cookies()
                    filtered_cookies = [ck for ck in all_cookies if ck.get("name") in REQUIRED_COOKIES]
                    self.save_cookies(account, filtered_cookies)
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login: cookies 已保存')
                    
                except Exception as e:
                    # 错误次数+1
                    self.err += 1
                    # 用f字符串格式化错误类型和错误信息，提供更多的调试信息
                    print(
                        f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login：页面加载或元素操作失败，错误类型：{type(e).__name__}, 详细错误信息：{str(e).split("Stacktrace:")[0]}'
                    )
        
                    # 保存错误截图
                    if enable_screenshot:
                        self.driver.save_screenshot(
                            f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                        )
                        
                    if self.err < max_retry_time:
                        # 刷新页面
                        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} login：刷新页面')
                        self.refresh_driver()
                        # 检查注意事项和验证码
                        if self.check_verification_code():
                            # 重试
                            self.login()
                    # 判断错误次数
                    if self.err >= max_retry_time:
                        print(
                            f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,login:重新尝试加载页面，这次指定需要重定向到首页'
                        )

    def get_page(self, reset_to_homepage=0):
        next_stage_flag = False
        try:
            if reset_to_homepage == 1:
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 尝试前往首页...')
                start_time = time.time()
                # 前往首页
                self.driver.get(
                    "https://flights.ctrip.com/online/channel/domestic")
                end_time = time.time()
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 前往首页耗时: {end_time - start_time:.2f} 秒')

            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 当前页面 URL: {self.driver.current_url}')
            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 当前页面标题: {self.driver.title}')

            # 检查注意事项和验证码
            if self.check_verification_code():
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 等待页面加载完成...')
                WebDriverWait(self.driver, max_wait_time).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "pc_home-jipiao"))
                )
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 页面加载完成')

                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 尝试点击飞机图标...')
                # 点击飞机图标，返回主界面
                ele = WebDriverWait(self.driver, max_wait_time).until(
                    element_to_be_clickable(
                        self.driver.find_element(
                            By.CLASS_NAME, "pc_home-jipiao")
                    )
                )
                ele.click()
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 成功点击飞机图标')

                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 尝试选择单程...')
                # 单程
                ele = WebDriverWait(self.driver, max_wait_time).until(
                    element_to_be_clickable(
                        self.driver.find_elements(
                            By.CLASS_NAME, "radio-label")[0]
                    )
                )
                ele.click()
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 成功选择单程')

                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 尝试点击搜索按钮...')
                # 搜索
                ele = WebDriverWait(self.driver, max_wait_time).until(
                    element_to_be_clickable(
                        self.driver.find_element(By.CLASS_NAME, "search-btn")
                    )
                )
                ele.click()
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 成功点击搜索按钮')

                next_stage_flag = True
        except Exception as e:
            # 用f字符串格式化错误类型和错误信息，提供更多的调试信息
            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} get_page：页面加载或元素操作失败，错误类型：{type(e).__name__}, 详细错误信息：{str(e).split("Stacktrace:")[0]}'
            )
            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 当前页面 URL: {self.driver.current_url}')
            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 当前页面标题: {self.driver.title}')
            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 当前页面源代码: {self.driver.page_source[:500]}...')  # 只打印前500个字符

            # 保存错误截图
            if enable_screenshot:
                screenshot_path = f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                self.driver.save_screenshot(screenshot_path)
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误截图已保存: {screenshot_path}')

            # 重新尝试加载页面，这次指定需要重定向到首页
            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 重新尝试加载页面，这次指定需要重定向到首页')
            self.get_page(1)
        else:
            if next_stage_flag:
                # 继续下一步
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 页面加载成功，继续下一步')
                self.change_city()
            else:
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 页面加载成功，但未能完成所有操作')

    def change_city(self):
        next_stage_flag = False
        try:
            # 等待页面完成加载
            WebDriverWait(self.driver, max_wait_time).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "form-input-v3"))
            )

            # 检查注意事项和验证码
            if self.check_verification_code():
                # 若出发地与目标值不符，则更改出发地
                while self.city[0] not in self.driver.find_elements(
                    By.CLASS_NAME, "form-input-v3"
                )[0].get_attribute("value"):
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[0]
                        )
                    )
                    ele.click()
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[0]
                        )
                    )
                    ele.send_keys(Keys.CONTROL + "a")
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[0]
                        )
                    )
                    ele.send_keys(self.city[0])

                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换城市【0】-{self.driver.find_elements(By.CLASS_NAME,"form-input-v3")[0].get_attribute("value")}'
                )

                # 若目的地与目标值不符，则更改目的地
                while self.city[1] not in self.driver.find_elements(
                    By.CLASS_NAME, "form-input-v3"
                )[1].get_attribute("value"):
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[1]
                        )
                    )
                    ele.click()
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[1]
                        )
                    )
                    ele.send_keys(Keys.CONTROL + "a")
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[1]
                        )
                    )
                    ele.send_keys(self.city[1])

                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换城市【1】-{self.driver.find_elements(By.CLASS_NAME,"form-input-v3")[1].get_attribute("value")}'
                )

                while (
                    self.driver.find_elements(By.CSS_SELECTOR, "[aria-label=请选择日期]")[
                        0
                    ].get_attribute("value")
                    != self.date
                ):
                    # 点击日期选择
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_element(
                                By.CLASS_NAME, "modifyDate.depart-date"
                            )
                        )
                    )
                    ele.click()

                    if int(
                        self.driver.find_elements(
                            By.CLASS_NAME, "date-picker.date-picker-block"
                        )[1]
                        .find_element(By.CLASS_NAME, "year")
                        .text[:-1]
                    ) < int(self.date[:4]):
                        ele = WebDriverWait(self.driver, max_wait_time).until(
                            element_to_be_clickable(
                                self.driver.find_elements(
                                    By.CLASS_NAME,
                                    "in-date-picker.icon.next-ico.iconf-right",
                                )[1]
                            )
                        )
                        print(
                            f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换日期{int(self.driver.find_elements(By.CLASS_NAME, "date-picker.date-picker-block")[1].find_element(By.CLASS_NAME, "year").text[:-1])}小于 {int(self.date[:4])} 向右点击'
                        )
                        ele.click()
                        
                    if int(
                        self.driver.find_elements(
                            By.CLASS_NAME, "date-picker.date-picker-block"
                        )[0]
                        .find_element(By.CLASS_NAME, "year")
                        .text[:-1]
                    ) > int(self.date[:4]):
                        ele = WebDriverWait(self.driver, max_wait_time).until(
                            element_to_be_clickable(
                                self.driver.find_elements(
                                    By.CLASS_NAME,
                                    "in-date-picker.icon.prev-ico.iconf-left",
                                )[0]
                            )
                        )
                        print(
                            f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换日期{int(self.driver.find_elements(By.CLASS_NAME, "date-picker.date-picker-block")[0].find_element(By.CLASS_NAME, "year").text[:-1])}大于 {int(self.date[:4])} 向左点击'
                        )
                        ele.click()

                    if int(
                        self.driver.find_elements(
                            By.CLASS_NAME, "date-picker.date-picker-block"
                        )[0]
                        .find_element(By.CLASS_NAME, "year")
                        .text[:-1]
                    ) == int(self.date[:4]):
                        if int(
                            self.driver.find_elements(
                                By.CLASS_NAME, "date-picker.date-picker-block"
                            )[0]
                            .find_element(By.CLASS_NAME, "month")
                            .text[:-1]
                        ) > int(self.date[5:7]):
                            ele = WebDriverWait(self.driver, max_wait_time).until(
                                element_to_be_clickable(
                                    self.driver.find_elements(
                                        By.CLASS_NAME,
                                        "in-date-picker.icon.prev-ico.iconf-left",
                                    )[0]
                                )
                            )
                            print(
                                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换日期{int(self.driver.find_elements(By.CLASS_NAME, "date-picker.date-picker-block")[0].find_element(By.CLASS_NAME, "month").text[:-1])}大于 {int(self.date[5:7])} 向左点击'
                            )
                            ele.click()
                            
                    if int(
                        self.driver.find_elements(
                            By.CLASS_NAME, "date-picker.date-picker-block"
                        )[1]
                        .find_element(By.CLASS_NAME, "year")
                        .text[:-1]
                    ) == int(self.date[:4]):
                        if int(
                            self.driver.find_elements(
                                By.CLASS_NAME, "date-picker.date-picker-block"
                            )[1]
                            .find_element(By.CLASS_NAME, "month")
                            .text[:-1]
                        ) < int(self.date[5:7]):
                            ele = WebDriverWait(self.driver, max_wait_time).until(
                                element_to_be_clickable(
                                    self.driver.find_elements(
                                        By.CLASS_NAME,
                                        "in-date-picker.icon.next-ico.iconf-right",
                                    )[1]
                                )
                            )
                            print(
                                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换日期{int(self.driver.find_elements(By.CLASS_NAME, "date-picker.date-picker-block")[1].find_element(By.CLASS_NAME, "month").text[:-1])}小于 {int(self.date[5:7])} 向右点击'
                            )
                            ele.click()

                    for m in self.driver.find_elements(
                        By.CLASS_NAME, "date-picker.date-picker-block"
                    ):
                        if int(m.find_element(By.CLASS_NAME, "year").text[:-1]) != int(
                            self.date[:4]
                        ):
                            continue

                        if int(m.find_element(By.CLASS_NAME, "month").text[:-1]) != int(
                            self.date[5:7]
                        ):
                            continue

                        for d in m.find_elements(By.CLASS_NAME, "date-d"):
                            if int(d.text) == int(self.date[-2:]):
                                ele = WebDriverWait(self.driver, max_wait_time).until(
                                    element_to_be_clickable(d)
                                )
                                ele.click()
                                break
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：更换日期-{self.driver.find_elements(By.CSS_SELECTOR,"[aria-label=请选择日期]")[0].get_attribute("value")}'
                )

                while "(" not in self.driver.find_elements(
                    By.CLASS_NAME, "form-input-v3"
                )[0].get_attribute("value"):
                    # Enter搜索
                    # ele=WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(its[1]))
                    # ele.send_keys(Keys.ENTER)
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[0]
                        )
                    )
                    ele.click()

                    # 通过低价提醒按钮实现enter键换页
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "low-price-remind"
                            )[0]
                        )
                    )
                    ele.click()

                while "(" not in self.driver.find_elements(
                    By.CLASS_NAME, "form-input-v3"
                )[1].get_attribute("value"):
                    # Enter搜索
                    # ele=WebDriverWait(self.driver, max_wait_time).until(element_to_be_clickable(its[1]))
                    # ele.send_keys(Keys.ENTER)
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "form-input-v3")[1]
                        )
                    )
                    ele.click()

                    # 通过低价提醒按钮实现enter键换页
                    ele = WebDriverWait(self.driver, max_wait_time).until(
                        element_to_be_clickable(
                            self.driver.find_elements(
                                By.CLASS_NAME, "low-price-remind"
                            )[0]
                        )
                    )
                    ele.click()

                next_stage_flag = True

        except Exception as e:
            # 错误次数+1
            self.err += 1

            # 保存错误截图
            if enable_screenshot:
                self.driver.save_screenshot(
                    f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                )

            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,change_city：更换城市和日期失败，错误类型：{type(e).__name__}, 详细错误信息：{str(e).split("Stacktrace:")[0]}'
            )

            # 检查注意事项和验证码
            if self.check_verification_code():
                if self.err < max_retry_time:
                    if len(self.driver.find_elements(By.CLASS_NAME, "lg_loginbox_modal")):
                        print(
                            f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：检测到登录弹窗，需要登录'
                        )
                        self.login()
                    # 重试
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：重试')
                    self.change_city()
                # 判断错误次数
                if self.err >= max_retry_time:
                    print(
                        f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,change_city:重新尝试加载页面，这次指定需要重定向到首页'
                    )

                    # 删除本次请求
                    del self.driver.requests

                    # 重置错误计数
                    self.err = 0

                    # 重新尝试加载页面，这次指定需要重定向到首页
                    self.get_page(1)
        else:
            if next_stage_flag:
                # 若无错误，执行下一步
                self.get_data()

                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} change_city：成功更换城市和日期，当前路线为：{self.city[0]}-{self.city[1]}')

    def get_data(self):
        try:
            # 等待响应加载完成
            self.predata = self.driver.wait_for_request(
                "/international/search/api/search/batchSearch?.*", timeout=max_wait_time
            )
            
            if comft_flight:
                # 捕获 getFlightComfort 数据
                self.comfort_data = self.capture_flight_comfort_data()
            
            rb = dict(json.loads(self.predata.body).get("flightSegments")[0])

        except Exception as e:
            # 错误次数+1
            self.err += 1

            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,get_data:获取数据超时，错误类型：{type(e).__name__}, 错误详细：{str(e).split("Stacktrace:")[0]}'
            )

            # 保存错误截图
            if enable_screenshot:
                self.driver.save_screenshot(
                    f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                )

            # 删除本次请求
            del self.driver.requests

            if self.err < max_retry_time:
                # 刷新页面
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} get_data：刷新页面')
                self.refresh_driver()

                # 检查注意事项和验证码
                if self.check_verification_code():
                    # 重试
                    self.get_data()

            # 判断错误次数
            if self.err >= max_retry_time:
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,get_data:重新尝试加载页面，这次指定需要重定向到首页'
                )

                # 重置错误计数
                self.err = 0
                # 重新尝试加载页面，这次指定需要重定向到首页
                self.get_page(1)
        else:
            # 删除本次请求
            del self.driver.requests

            # 检查数据获取正确性
            if (
                rb["departureCityName"] == self.city[0]
                and rb["arrivalCityName"] == self.city[1]
                and rb["departureDate"] == self.date
            ):
                print(f"get_data:城市匹配成功：出发地-{self.city[0]}，目的地-{self.city[1]}")

                # 重置错误计数
                self.err = 0

                # 若无错误，执行下一步
                self.decode_data()
            else:
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,get_data:刷新页面')
                # 错误次数+1
                self.err += 1

                # 保存错误截图
                if enable_screenshot:
                    self.driver.save_screenshot(
                        f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                    )

                # 重新更换城市
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} get_data：重新更换城市:{rb["departureCityName"]}-{rb["arrivalCityName"]}-{rb["departureDate"]}'
                )

                # 检查注意事项和验证码
                if self.check_verification_code():
                    # 重试
                    self.change_city()

    def decode_data(self):
        try:
            # 使用python-magic库检查MIME类型
            mime = magic.Magic()
            file_type = mime.from_buffer(self.predata.response.body)

            buf = io.BytesIO(self.predata.response.body)

            if "gzip" in file_type:
                gf = gzip.GzipFile(fileobj=buf)
                self.dedata = gf.read().decode("UTF-8")
            elif "JSON data" in file_type:
                print(buf.read().decode("UTF-8"))
            else:
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 未知的压缩格式：{file_type}')
            
            self.dedata = json.loads(self.dedata)

        except Exception as e:
            # 错误次数+1
            self.err += 1

            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,decode_data:数据解码失败，错误类型：{type(e).__name__}, 错误详细：{str(e).split("Stacktrace:")[0]}'
            )

            # 保存错误截图
            if enable_screenshot:
                self.driver.save_screenshot(
                    f'screenshot/screenshot_{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                )

            # 删除本次请求
            del self.driver.requests

            if self.err < max_retry_time:
                # 刷新页面
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} decode_data：刷新页面')
                self.refresh_driver()

                # 检查注意事项和验证码
                if self.check_verification_code():
                    # 重试
                    self.get_data()
            # 判错错误次数
            if self.err >= max_retry_time:
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,decode_data:重新尝试加载页面，这次指定需要重定向到首页'
                )

                # 重置错误计数
                self.err = 0

                # 重新尝试加载页面，这次指定需要重定向到首页
                self.get_page(1)
        else:
            # 重置错误计数
            self.err = 0

            # 若无错误，执行下一步
            self.check_data()

    def check_data(self):
        try:
            self.flightItineraryList = self.dedata["data"]["flightItineraryList"]
            # 倒序遍历,删除转机航班
            for i in range(len(self.flightItineraryList) - 1, -1, -1):
                if (
                    self.flightItineraryList[i]["flightSegments"][0]["transferCount"]
                    != 0
                ):
                    self.flightItineraryList.pop(i)
            if len(self.flightItineraryList) == 0 and direct_flight:
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 不存在直航航班:{self.city[0]}-{self.city[1]}')
                # 重置错误计数
                self.err = 0
                return 0
        except Exception as e:
            # 错误次数+1
            self.err += 1
            print(
                f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 数据检查出错：不存在航班，错误类型：{type(e).__name__}, 错误详细：{str(e).split("Stacktrace:")[0]}'
            )
            print(self.dedata)
            if self.err < max_retry_time:
                if 'searchErrorInfo' in self.dedata["data"]:
                    # 重置错误计数
                    self.err = 0
                    return 0
                else:
                    if "'needUserLogin': True" in str(self.dedata["data"]):
                        print(
                            f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,check_data:必须要登录才能查看数据，这次指定需要重定向到首页'
                        )
                        # 重新尝试加载页面，这次指定需要重定向到首页
                        self.login()
                    
                    # 刷新页面
                    print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} check_data：刷新页面')
                    self.refresh_driver()
                    # 检查注意事项和验证码
                    if self.check_verification_code():
                        # 重试
                        self.get_data()
            # 判断错误次数
            if self.err >= max_retry_time:
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 错误次数【{self.err}-{max_retry_time}】,check_data:重新尝试加载页面，这次指定需要重定向到首页'
                )

                # 重置错误计数
                self.err = 0

                # 重新尝试加载页面，这次指定需要重定向到首页
                self.get_page(1)
        else:
            # 重置错误计数
            self.err = 0
            self.proc_flightSegments()
            self.proc_priceList()
            self.mergedata()

    def proc_flightSegments(self):
        self.flights = pd.DataFrame()

        for flightlist in self.flightItineraryList:
            flightlist = flightlist["flightSegments"][0]["flightList"]
            flightUnitList = dict(flightlist[0])

            departureday = flightUnitList["departureDateTime"].split(" ")[0]
            departuretime = flightUnitList["departureDateTime"].split(" ")[1]

            arrivalday = flightUnitList["arrivalDateTime"].split(" ")[0]
            arrivaltime = flightUnitList["arrivalDateTime"].split(" ")[1]

            # 处理 stopList
            if 'stopList' in flightUnitList and flightUnitList['stopList']:
                stop_info = []
                for stop in flightUnitList['stopList']:
                    stop_info.append(f"{stop['cityName']}({stop['airportName']}, {stop['duration']}分钟)")
                flightUnitList['stopInfo'] = ' -> '.join(stop_info)
            else:
                flightUnitList['stopInfo'] = '无中转'

            if del_info:
                # 删除一些不重要的信息
                dellist = [
                    "sequenceNo",
                    "marketAirlineCode",
                    "departureProvinceId",
                    "departureCityId",
                    "departureCityCode",
                    "departureAirportShortName",
                    "departureTerminal",
                    "arrivalProvinceId",
                    "arrivalCityId",
                    "arrivalCityCode",
                    "arrivalAirportShortName",
                    "arrivalTerminal",
                    "transferDuration",
                    "stopList",
                    "leakedVisaTagSwitch",
                    "trafficType",
                    "highLightPlaneNo",
                    "mealType",
                    "operateAirlineCode",
                    "arrivalDateTime",
                    "departureDateTime",
                    "operateFlightNo",
                    "operateAirlineName",
                ]
                for value in dellist:
                    flightUnitList.pop(value, None)

            # 更新日期格式
            flightUnitList.update(
                {
                    "departureday": departureday,
                    "departuretime": departuretime,
                    "arrivalday": arrivalday,
                    "arrivaltime": arrivaltime,
                }
            )

            self.flights = pd.concat(
                [
                    self.flights,
                    pd.DataFrame.from_dict(flightUnitList, orient="index").T,
                ],
                ignore_index=True,
            )

    def proc_priceList(self):
        self.prices = pd.DataFrame()

        for flightlist in self.flightItineraryList:
            flightNo = flightlist["itineraryId"].split("_")[0]
            priceList = flightlist["priceList"]

            # 经济舱，经济舱折扣
            economy, economy_tax, economy_total, economy_full = [], [], [], []
            economy_origin_price, economy_tax_price, economy_total_price, economy_full_price = "", "", "", ""
            # 商务舱，商务舱折扣
            bussiness, bussiness_tax, bussiness_total, bussiness_full = [], [], [], []
            bussiness_origin_price, bussiness_tax_price, bussiness_total_price, bussiness_full_price = "", "", "", ""

            for price in priceList:
                # print("Price dictionary keys:", price.keys())
                # print("Full price dictionary:", json.dumps(price, indent=2))
                
                adultPrice = price["adultPrice"]
                childPrice = price.get("childPrice", adultPrice)  # 如果没有childPrice，使用adultPrice
                freeOilFeeAndTax = price["freeOilFeeAndTax"]
                sortPrice = price.get("sortPrice", adultPrice)  # 如果没有sortPrice，使用adultPrice
                
                # 估算税费（如果需要的话）
                estimatedTax = sortPrice - adultPrice if not freeOilFeeAndTax else 0
                adultTax = price.get("adultTax", estimatedTax)  # 如果没有adultTax，使用estimatedTax

                miseryIndex = price["miseryIndex"]
                cabin = price["cabin"]

                # 经济舱
                if cabin == "Y":
                    economy.append(adultPrice)
                    economy_tax.append(adultTax)
                    economy_full.append(miseryIndex)
                    economy_total.append(adultPrice+adultTax)
                # 商务舱
                elif cabin == "C":
                    bussiness.append(adultPrice)
                    bussiness_tax.append(adultTax)
                    bussiness_full.append(miseryIndex)
                    bussiness_total.append(adultPrice+adultTax)

            # 初始化变量
            economy_min_index = None
            bussiness_min_index = None
            
            if economy_total != []:
                economy_total_price = min(economy_total)
                economy_min_index = economy_total.index(economy_total_price)
            
            if bussiness_total != []:
                bussiness_total_price = min(bussiness_total)
                bussiness_min_index = bussiness_total.index(bussiness_total_price)
            
            if economy_min_index is not None:
                economy_origin_price = economy[economy_min_index]
                economy_tax_price = economy_tax[economy_min_index]
                economy_full_price = economy_full[economy_min_index]
            
            if bussiness_min_index is not None:
                bussiness_origin_price = bussiness[bussiness_min_index]
                bussiness_tax_price = bussiness_tax[bussiness_min_index]
                bussiness_full_price = bussiness_full[bussiness_min_index]
            
            price_info = {
                "flightNo": flightNo,
                "economy_origin": economy_origin_price,
                "economy_tax": economy_tax_price,
                "economy_total": economy_total_price,
                "economy_full": economy_full_price,
                "bussiness_origin": bussiness_origin_price,
                "bussiness_tax": bussiness_tax_price,
                "bussiness_total": bussiness_total_price,
                "bussiness_full": bussiness_full_price,
            }

            # self.prices=self.prices.append(price_info,ignore_index=True)
            self.prices = pd.concat(
                [self.prices, pd.DataFrame(price_info, index=[0])], ignore_index=True
            )

    def mergedata(self):
        try:
            self.df = self.flights.merge(self.prices, on=["flightNo"])
            print(f"合并后的航班数据形状: {self.df.shape}")
            print(f"合并后的航班数据列: {self.df.columns}")

            self.df["dateGetTime"] = dt.now().strftime("%Y-%m-%d")

            print(f"获取到的舒适度数据: {self.comfort_data}")
            
            # 数据的列名映射
            columns = {
                "dateGetTime": "数据获取日期",
                "flightNo": "航班号",
                "marketAirlineName": "航空公司",
                "departureday": "出发日期",
                "departuretime": "出发时间",
                "arrivalday": "到达日期",
                "arrivaltime": "到达时间",
                "duration": "飞行时长",
                "departureCountryName": "出发国家",
                "departureCityName": "出发城市",
                "departureAirportName": "出发机场",
                "departureAirportCode": "出发机场三字码",
                "arrivalCountryName": "到达国家",
                "arrivalCityName": "到达城市",
                "arrivalAirportName": "到达机场",
                "arrivalAirportCode": "到达机场三字码",
                "aircraftName": "飞机型号",
                "aircraftSize": "飞机尺寸",
                "aircraftCode": "飞机型号三字码",
                "arrivalPunctuality": "到达准点率",
                "stopCount": "停留次数",
                "stopInfo": "中转信息"
            }
            
            # 定义舒适度数据的列名映射
            comfort_columns = {
                'departure_delay_time': '出发延误时间',
                'departure_bridge_rate': '出发廊桥率',
                'arrival_delay_time': '到达延误时间',
                'plane_type': '飞机类型',
                'plane_width': '飞机宽度',
                'plane_age': '飞机机龄',
                'Y_has_meal': '经济舱是否有餐食',
                'Y_seat_tilt': '经济舱座椅倾斜度',
                'Y_seat_width': '经济舱座椅宽度',
                'Y_seat_pitch': '经济舱座椅间距',
                'Y_meal_msg': '经济舱餐食信息',
                'Y_power': '经济舱电源',
                'C_has_meal': '商务舱是否有餐食',
                'C_seat_tilt': '商务舱座椅倾斜度',
                'C_seat_width': '商务舱座椅宽度',
                'C_seat_pitch': '商务舱座椅间距',
                'C_meal_msg': '商务舱餐食信息',
                'C_power': '商务舱电源',
            }
            
            if self.comfort_data:
                comfort_df = pd.DataFrame.from_dict(self.comfort_data, orient='index')
                comfort_df.reset_index(inplace=True)
                comfort_df.rename(columns={'index': 'flight_no'}, inplace=True)
                
                print(f"舒适度数据形状: {comfort_df.shape}")
                print(f"舒适度数据列: {comfort_df.columns}")
                print(f"舒适度数据前几行: \n{comfort_df.head()}")
                
                # 检查 operateFlightNo 列是否存在
                if 'operateFlightNo' in self.df.columns:
                    print(f"合并前的 operateFlightNo 唯一值: {self.df['operateFlightNo'].unique()}")
                    # 创建一个临时列来存储用于匹配的航班号
                    self.df['match_flight_no'] = self.df['operateFlightNo'].fillna(self.df['flightNo'])
                else:
                    print("警告: operateFlightNo 列不存在于数据中,将使用 flightNo 进行匹配")
                    self.df['match_flight_no'] = self.df['flightNo']
                
                print(f"现有的列: {self.df.columns}")
                print(f"合并前的 flight_no 唯一值: {comfort_df['flight_no'].unique()}")
                
                # 使用 left join 来合并数据
                self.df = self.df.merge(comfort_df, left_on='match_flight_no', right_on='flight_no', how='left')
                
                print(f"合并后的数据形状: {self.df.shape}")
                print(f"合并后的数据列: {self.df.columns}")
                
                # 删除临时列和多余的flight_no列
                self.df.drop(['match_flight_no', 'flight_no'], axis=1, inplace=True, errors='ignore')
            else:
                # 如果没有舒适度数据，手动添加空列，保证数据结构一致性
                for col in comfort_columns.keys():
                    self.df[col] = None  # 添加缺失的舒适度列并填充为空值

            if rename_col:
                order = list(columns.values())
                # 对pandas的columns进行重命名
                columns.update(comfort_columns, errors='ignore')

                self.df = self.df.rename(columns=columns)

                if del_info:
                    # 使用 reindex 确保所有列都存在于最终的 DataFrame 中，不存在的列会被自动忽略
                    self.df = self.df.reindex(columns=order, fill_value=None)

            files_dir = os.path.join(
                os.getcwd(), self.date, dt.now().strftime("%Y-%m-%d")
            )

            if not os.path.exists(files_dir):
                os.makedirs(files_dir)

            filename = os.path.join(
                files_dir, f"{self.city[0]}-{self.city[1]}.csv")

            self.df.to_csv(filename, encoding="UTF-8", index=False)

            print(f'\n{time.strftime("%Y-%m-%d_%H-%M-%S")} 数据爬取完成 {filename}\n')

            return 0

        except Exception as e:
            print(f"合并数据失败 {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误详情: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return 0

    def capture_flight_comfort_data(self):
        try:
            # 滚动页面到底部以加载所有内容
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # 分步滚动页面
                for i in range(10):  # 将页面分成10步滚动
                    scroll_height = last_height * (i + 1) / 3
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                    time.sleep(0.5)  # 每一小步等待0.5秒
                
                # 等待页面加载
                time.sleep(3)  # 滚动到底部后多等待3秒
                
                # 计算新的滚动高度并与最后的滚动高度进行比较
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            comfort_requests = self.driver.requests
            comfort_data = {}
            batch_comfort_found = False
            getFlightComfort_requests_count = 0
            total_requests_count = len(comfort_requests)

            print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')} 开始分析请求，总请求数：{total_requests_count}")

            for request in comfort_requests:
                if "/search/api/flight/comfort/batchGetComfortTagList" in request.url:
                    batch_comfort_found = True
                    print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 找到 batchGetComfortTagList 请求")
                    continue
                
                if "/search/api/flight/comfort/getFlightComfort" in request.url:
                    getFlightComfort_requests_count += 1
                    print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')} 捕获到第 {getFlightComfort_requests_count} 个 getFlightComfort 请求:")
                    print(f"URL: {request.url}")
                    
                    try:
                        payload = json.loads(request.body.decode('utf-8'))
                        flight_no = payload.get('flightNoList', ['Unknown'])[0]
                        print(f"请求的航班号: {flight_no}")
                    except Exception as e:
                        print(f"无法解析请求 payload: {str(e)}")
                        continue

                    if request.response:
                        print(f"响应状态码: {request.response.status_code}")
                        body = request.response.body
                        if request.response.headers.get('Content-Encoding', '').lower() == 'gzip':
                            body = gzip.decompress(body)
                        
                        try:
                            json_data = json.loads(body.decode('utf-8'))
                            print(f"响应数据: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")  # 打印前500个字符
                            if json_data['status'] == 0 and json_data['msg'] == 'success':
                                flight_comfort = json_data['data']
                                
                                punctuality = flight_comfort['punctualityInfo']
                                plane_info = flight_comfort['planeInfo']
                                cabin_info = {cabin['cabin']: cabin for cabin in flight_comfort['cabinInfoList']}
                                
                                processed_data = {
                                    'departure_delay_time': punctuality.get("departureDelaytime", None),
                                    'departure_bridge_rate': punctuality.get("departureBridge", None),
                                    'arrival_delay_time': punctuality.get("arrivalDelaytime", None),
                                    'plane_type': plane_info.get("planeTypeName", None),
                                    'plane_width': plane_info.get("planeWidthCategory", None),
                                    'plane_age': plane_info.get("planeAge", None)
                                }
                                
                                for cabin_type in ['Y', 'C']:
                                    if cabin_type in cabin_info:
                                        cabin = cabin_info[cabin_type]
                                        processed_data.update({
                                            f'{cabin_type}_has_meal': cabin['hasMeal'],
                                            f'{cabin_type}_seat_tilt': cabin['seatTilt']['value'],
                                            f'{cabin_type}_seat_width': cabin['seatWidth']['value'],
                                            f'{cabin_type}_seat_pitch': cabin['seatPitch']['value'],
                                            f'{cabin_type}_meal_msg': cabin['mealMsg']
                                        })
                                        if 'power' in cabin:
                                            processed_data[f'{cabin_type}_power'] = cabin['power']
                                
                                comfort_data[flight_no] = processed_data
                                print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 成功提取航班 {flight_no} 的舒适度数据")
                            else:
                                print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} getFlightComfort 响应状态异常: {json_data['status']}, {json_data['msg']}")
                        except Exception as e:
                            print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 处理 getFlightComfort 响应时出错: {str(e)}")
                    else:
                        print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} getFlightComfort 请求没有响应")

            print(f"\n{time.strftime('%Y-%m-%d_%H-%M-%S')} 请求分析完成")
            print(f"总请求数: {total_requests_count}")
            print(f"batchGetComfortTagList 请求是否找到: {batch_comfort_found}")
            print(f"getFlightComfort 请求数: {getFlightComfort_requests_count}")
            print(f"成功提取的舒适度数据数: {len(comfort_data)}")

            if comfort_data:
                # 创建舒适度DataFrame
                comfort_df = pd.DataFrame.from_dict(comfort_data, orient='index')
                comfort_df.reset_index(inplace=True)
                comfort_df.rename(columns={'index': 'flight_no'}, inplace=True)
                
                # 保存舒适度数据为CSV文件
                # save_dir = os.path.join(os.getcwd(), self.date, datetime.now().strftime("%Y-%m-%d"))
                # os.makedirs(save_dir, exist_ok=True)
                
                # comfort_filename = os.path.join(save_dir, f"{self.city[0]}-{self.city[1]}_comfort.csv")
                # comfort_df.to_csv(comfort_filename, encoding="UTF-8", index=False)
                # print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 航班舒适度数据已保存到 {comfort_filename}")
                
                return comfort_data
            else:
                print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 未捕获到任何 getFlightComfort 数据")
                print("可能的原因:")
                print("1. 网页没有加载完全")
                print("2. 网站结构可能已经改变")
                print("3. 网络连接问题")
                print("4. 请求被网站拦截或限制")
                return None

        except Exception as e:
            print(f"{time.strftime('%Y-%m-%d_%H-%M-%S')} 捕获 getFlightComfort 数据时出错：{str(e)}")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误详情: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return None


if __name__ == "__main__":

    driver = init_driver()

    citys = gen_citys(crawl_citys)

    flight_dates = generate_flight_dates(crawl_days, begin_date, end_date, start_interval, days_interval)

    Flight_DataFetcher = DataFetcher(driver)

    for city in citys:
        Flight_DataFetcher.city = city

        for flight_date in flight_dates:
            Flight_DataFetcher.date = flight_date

            if os.path.exists(os.path.join(os.getcwd(), flight_date, dt.now().strftime("%Y-%m-%d"), f"{city[0]}-{city[1]}.csv")):
                print(
                    f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 文件已存在:{os.path.join(os.getcwd(), flight_date, dt.now().strftime("%Y-%m-%d"), f"{city[0]}-{city[1]}.csv")}')
                continue
            elif ('http' not in Flight_DataFetcher.driver.current_url):
                print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} 当前的URL是：{driver.current_url}')
                # 初始化页面
                Flight_DataFetcher.get_page(1)

            else:
                # 后续运行只需更换出发与目的地
                Flight_DataFetcher.change_city()

            time.sleep(crawl_interval)

    # 运行结束退出
    try:
        driver = Flight_DataFetcher.driver
        driver.quit()
    except Exception as e:
        print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")} An error occurred while quitting the driver: {e}')

    print(f'\n{time.strftime("%Y-%m-%d_%H-%M-%S")} 程序运行完成！！！！')

# %% [notebook cell 15]
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
 
from selenium.webdriver.edge.options import Options
 
def to_the_buttom():
    js = 'document.getElementsByClassName("search-body left_is_mini")[0].scrollTop=10000'
    driver.execute_script(js)
def to_the_top():
    js = "var q=document.documentElement.scrollTop=0"  # 滚动到最上面
    driver.execute_script(js)
def to_deal_question():
    driver.implicitly_wait(10)
    time.sleep(3)
    to_the_buttom()
    time.sleep(3)
def to_view():
    driver.implicitly_wait(10)
    to_the_buttom()
    time.sleep(3)
    button = driver.find_element(By.XPATH, '//*[@id="commentModule"]/div[6]/ul/li[7]/a')
    driver.execute_script("arguments[0].scrollIntoView();", button)
 
opt = Options()
opt.add_argument("--headless")
opt.add_argument("window-size=1920x1080")
opt.add_argument('--start-maximized')
driver = webdriver.Edge(options=opt)
url = 'https://www.ly.com/scenery/BookSceneryTicket_45701.html'
driver.get(url)
# driver.maximize_window()
 
#  add_argument() 方法添加参数
 
print(1)
with open("小七孔.txt", "a", encoding='utf-8') as f:
    for x in range(3,9):
        driver.implicitly_wait(10)
        # to_the_buttom()
        time.sleep(3)
        # to_the_buttom()
        for i in range(10):
             text = driver.find_elements(By.CLASS_NAME, "dpdetail")[i].text
             f.write(text)
             f.write("\n")
        print(x)
        button = driver.find_element(By.XPATH, '//*[@id="pageNum_title"]/div[2]/div/a[{}]'.format(x))
        button.click()
with open("小七孔.txt", "a", encoding='utf-8') as f:
    for x in range(9,60):
        driver.implicitly_wait(10)
        # to_the_buttom()
        time.sleep(3)
        # to_the_buttom()
        for i in range(10):
            text = driver.find_elements(By.CLASS_NAME, "dpdetail")[i].text
            f.write(text)
            f.write("\n")
        print(x)
        button = driver.find_element(By.XPATH, '//*[@id="pageNum_title"]/div[2]/div/a[7]')
        button.click()
time.sleep(1000)
driver.close()

# %% [notebook cell 17]
import jieba
stopwords = [line.strip() for line in open('stopwords.txt',encoding='utf-8').readlines()]
stopwords.append("\n")
# print(stopwords)
f1=open('小七孔.txt','r',encoding='utf-8')
code=[]
for i in f1.read().strip().split(' '):
    words = jieba.lcut(i)
    code+=words
d={}
for word in code:
    if word not in stopwords:
        d[word]=d.get(word,0)+1
ls=list(d.items())
ls.sort(key=lambda s:s[-1],reverse=True)
print(ls)
f1.close()
with open("小七孔.txt", "a", encoding='utf-8') as f:
    for i in range(20):
        f.write(str(ls[i]))
        f.write("\n")

# %% [notebook cell 18]
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba

# 打开文本
text = open("小七孔.txt", encoding="utf-8").read()
# 替换"展开全部"
text = text.replace("展开全部", "")

# 中文分词（可选：如果你希望先分词再生成词云）
# text = ' '.join(jieba.cut(text))

# 设置词云参数
wc = WordCloud(
    font_path="msyh.ttc",           # 中文字体路径
    width=800,
    height=600,
    mode="RGBA",
    background_color=None,          # 透明背景
    max_font_size=65,               # 控制最大字体大小（避免太大）
    min_font_size=15,               # 最小字体不要太小
    relative_scaling=0.3,           # 字体大小与频率之间的相关性减弱（值越小，差异越小）
    prefer_horizontal=0.9,          # 水平显示词语的比例（0.9 表示大多数是水平的）
    collocations=False              # 禁止重复双词组合（防止重复词出现）
).generate(text)

# 显示词云
plt.figure(figsize=(30, 20))
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

# 保存到文件
wc.to_file("小七孔.png")

# %% [notebook cell 19]
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:44:00 2025

@author: Airble Dellen
简化版：爬取景点名称、评分和评分人数
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains 
import time
from bs4 import BeautifulSoup
import csv
import os
import re

def save_attraction_data(attractions_data):
    """保存景点数据到CSV文件"""
    filename = "贵州景点评分.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["景点名称", "评分", "评分人数"])
        for attraction in attractions_data:
            writer.writerow([attraction['name'], attraction['score'], attraction['review_count']])

def extract_attraction_info(driver):
    """从当前页面提取景点信息"""
    attractions = []
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    # 查找所有景点卡片
    attraction_cards = soup.find_all("div", class_="gsl-common-card")
    
    for card in attraction_cards:
        try:
            # 提取景点名称
            name_elem = card.find("p", class_="title")
            if name_elem:
                name = name_elem.get_text(strip=True)
            else:
                continue
            
            # 初始化评分和评分人数
            score = "暂无评分"
            review_count = "暂无评分人数"
            
            # 提取评分和评分人数 - 根据HTML结构
            tag_elem = card.find("p", class_="tag")
            if tag_elem:
                # 获取所有span元素
                spans = tag_elem.find_all("span")
                
                for span in spans:
                    span_text = span.get_text(strip=True)
                    
                    # 提取评分（如：4.4分）
                    if re.match(r'^\d+\.\d+分?$', span_text) or re.match(r'^\d+\.\d+$', span_text):
                        score = span_text if span_text.endswith('分') else span_text + "分"
                    
                    # 提取评分人数（如：472条评论、1234人评价、5678条点评等）
                    review_match = re.search(r'(\d+)(?:条评论|人评价|条点评|条评价|人点评)', span_text)
                    if review_match:
                        review_count = review_match.group(0)
            
            # 如果在tag中没找到，尝试在整个卡片中查找
            if score == "暂无评分" or review_count == "暂无评分人数":
                card_text = card.get_text()
                
                # 查找评分
                if score == "暂无评分":
                    score_match = re.search(r'(\d+\.\d+)分?', card_text)
                    if score_match:
                        score = score_match.group(1) + "分"
                
                # 查找评分人数
                if review_count == "暂无评分人数":
                    review_match = re.search(r'(\d+)(?:条评论|人评价|条点评|条评价|人点评)', card_text)
                    if review_match:
                        review_count = review_match.group(0)
            
            attractions.append({
                'name': name,
                'score': score,
                'review_count': review_count
            })
            
            print(f"景点: {name}, 评分: {score}, 评分人数: {review_count}")
            
        except Exception as e:
            print(f"提取景点信息时出错: {e}")
            continue
    
    return attractions

# 主程序
def main():
    service = Service(r"F:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
        # 访问贵州景点搜索页面
        driver.get("https://you.ctrip.com/globalsearch/?keyword=%E8%B4%B5%E5%B7%9E%E6%99%AF%E7%82%B9")
        print("页面标题:", driver.title)
        time.sleep(3)

        # 点击"更多"按钮展开更多景点
        try:
            gslmore = driver.find_element(By.ID, "home-page-travel-list").find_element(By.CLASS_NAME, "gsl-more")
            actions = ActionChains(driver)
            actions.click(gslmore)
            actions.perform()
            time.sleep(3)
            print("点击了更多按钮")
        except Exception as e:
            print(f"点击更多按钮失败: {e}")

        all_attractions = []

        # 爬取多页数据
        for page_num in range(1, 11):
            print(f"\n正在爬取第 {page_num} 页...")
            
            try:
                # 如果不是第一页，需要输入页码
                if page_num > 1:
                    try:
                        # 输入页码
                        page_input = driver.find_element(By.XPATH, '//input[@aria-label="页"]')
                        page_input.clear()
                        page_input.send_keys(str(page_num))
                        page_input.send_keys(Keys.RETURN)
                        time.sleep(3)
                    except Exception as e:
                        print(f"翻页失败: {e}")
                        # 尝试点击下一页按钮
                        try:
                            next_button = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')] | //button[contains(text(), '下一页')] | //*[contains(@class, 'next')]")
                            next_button.click()
                            time.sleep(3)
                        except:
                            print(f"无法翻到第 {page_num} 页")
                            break
                
                # 提取当前页面的景点信息
                attractions = extract_attraction_info(driver)
                if attractions:
                    all_attractions.extend(attractions)
                    print(f"第 {page_num} 页获取到 {len(attractions)} 个景点")
                else:
                    print(f"第 {page_num} 页未获取到景点数据")
                    # 如果连续几页都没有数据，可能已到末尾
                    if page_num > 3:
                        break
                
            except Exception as e:
                print(f"处理第 {page_num} 页时出错: {e}")
                continue

        # 保存所有数据
        if all_attractions:
            save_attraction_data(all_attractions)
            print(f"\n爬取完成！共获取到 {len(all_attractions)} 个景点信息")
            print("数据已保存到 '贵州景点评分.csv' 文件")
        else:
            print("未获取到任何景点数据，请检查页面结构或网络连接")

    except Exception as e:
        print(f"程序执行出错: {e}")

    finally:
        driver.quit()
        print("浏览器已关闭")

# 运行主程序
if __name__ == "__main__":
    main()
