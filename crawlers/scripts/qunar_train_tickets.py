# -*- coding: utf-8 -*-
"""Qunar train-ticket Selenium crawler.

Generated from: all_train_ticket.ipynb
Notebook outputs are intentionally omitted; only source code cells are kept.
"""

# %% [notebook cell 1]
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import csv
import time
import os
from datetime import datetime

class TrainTicketScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # 贵州主要城市列表
        self.guizhou_cities = [
            "贵阳", "遵义", "六盘水", "安顺", "毕节", 
            "铜仁", "黔东南", "黔南", "黔西南", "凯里",
            "都匀", "兴义", "赤水", "仁怀", "清镇"
        ]
    
    def get_driver(self):
        """获取Chrome驱动"""
        return webdriver.Chrome(options=self.chrome_options)
    
    def scrape_route(self, from_station, to_station, date="2025-06-05"):
        """抓取指定路线的火车票信息"""
        driver = self.get_driver()
        trains = []
        
        try:
            url = f"https://train.qunar.com/stationToStation.htm?fromStation={from_station}&toStation={to_station}&date={date}"
            print(f"正在抓取: {from_station} -> {to_station}")
            
            driver.get(url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 尝试等待列车信息加载
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testdt], .train-item"))
                )
            except:
                print(f"等待页面加载超时: {from_station} -> {to_station}")
            
            html = driver.page_source
            doc = pq(html)
            
            # 尝试多种选择器
            train_selectors = [
                'li[data-testdt]',
                '.train-item',
                '.search-result-item',
                '.list-item'
            ]
            
            for selector in train_selectors:
                items = doc(selector)
                if items:
                    print(f"找到 {len(items)} 个车次 (使用选择器: {selector})")
                    break
            
            for item in items.items():
                train_info = self.extract_train_info(item, from_station, to_station)
                if train_info and train_info.get("车次"):
                    trains.append(train_info)
            
            if not trains:
                print(f"未找到车次信息: {from_station} -> {to_station}")
                # 保存HTML用于调试
                with open(f"debug_{from_station}_{to_station}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
        except Exception as e:
            print(f"抓取出错 {from_station} -> {to_station}: {str(e)}")
        finally:
            driver.quit()
            
        return trains
    
    def extract_train_info(self, item, from_station, to_station):
        """提取单个车次信息"""
        try:
            train = {
                "路线": f"{from_station} -> {to_station}",
                "车次": self.safe_text(item, '.js-trainNum, .train-num, .trainNum'),
                "出发站": self.safe_text(item, '.start span:first, .dep-station, .from-station') or from_station,
                "到达站": self.safe_text(item, '.end span:first, .arr-station, .to-station') or to_station,
                "出发时间": self.safe_text(item, '.startime, .dep-time, .start-time'),
                "到达时间": self.safe_text(item, '.endtime, .arr-time, .end-time'),
                "历时": self.safe_text(item, '.duration, .travel-time'),
                "二等座价格": self.get_seat_price(item, "二等座"),
                "一等座价格": self.get_seat_price(item, "一等座"),
                "商务座价格": self.get_seat_price(item, "商务座"),
                "硬座价格": self.get_seat_price(item, "硬座"),
                "硬卧价格": self.get_seat_price(item, "硬卧"),
                "软卧价格": self.get_seat_price(item, "软卧"),
                "无座价格": self.get_seat_price(item, "无座"),
                "二等座余票": self.get_seat_count(item, 0),
                "一等座余票": self.get_seat_count(item, 1),
                "商务座余票": self.get_seat_count(item, 2),
                "抓取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return train
        except Exception as e:
            print(f"提取车次信息出错: {str(e)}")
            return None
    
    def safe_text(self, item, selectors):
        """安全获取文本内容"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                text = item.find(selector).text().strip()
                if text:
                    return text
            except:
                continue
        return "无"
    
    def get_seat_price(self, item, seat_type):
        """获取座位价格"""
        try:
            price_selectors = [
                f'.ticketed:contains("{seat_type}") .price',
                f'.seat-info:contains("{seat_type}") .price',
                f'[data-seat-type="{seat_type}"] .price'
            ]
            
            for selector in price_selectors:
                price = item.find(selector).text().strip()
                if price and price != "无":
                    return price
            return "无"
        except:
            return "无"
    
    def get_seat_count(self, item, index):
        """获取余票数量"""
        try:
            count_selectors = [
                f'.surplus span:eq({index})',
                f'.seat-count:eq({index})',
                f'.ticket-count:eq({index})'
            ]
            
            for selector in count_selectors:
                count = item.find(selector).text().strip()
                if count:
                    return count
            return "无"
        except:
            return "无"
    
    def save_to_csv(self, trains, filename):
        """保存到CSV文件"""
        if not trains:
            print(f"没有数据保存到 {filename}")
            return
        
        os.makedirs("train_data", exist_ok=True)
        filepath = os.path.join("train_data", filename)
        
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=trains[0].keys())
            writer.writeheader()
            writer.writerows(trains)
        
        print(f"成功保存 {len(trains)} 条数据到 {filepath}")
    
    def scrape_shanghai_to_guiyang(self, date="2025-06-05"):
        """抓取上海到贵阳的车票"""
        print("=" * 50)
        print("开始抓取：上海 -> 贵阳")
        print("=" * 50)
        
        trains = self.scrape_route("上海", "贵阳", date)
        if trains:
            self.save_to_csv(trains, f"上海到贵阳_{date}.csv")
        return trains
    
    def scrape_guiyang_to_guizhou_cities(self, date="2025-06-05"):
        """抓取贵阳到贵州各城市的车票"""
        print("=" * 50)
        print("开始抓取：贵阳 -> 贵州各城市")
        print("=" * 50)
        
        all_trains = []
        for city in self.guizhou_cities:
            if city != "贵阳":  # 跳过贵阳自己
                trains = self.scrape_route("贵阳", city, date)
                all_trains.extend(trains)
                time.sleep(2)  # 避免请求过于频繁
        
        if all_trains:
            self.save_to_csv(all_trains, f"贵阳到贵州各城市_{date}.csv")
        return all_trains
    
    def scrape_shanghai_to_guizhou_cities(self, date="2025-06-05"):
        """抓取上海到贵州各城市的车票"""
        print("=" * 50)
        print("开始抓取：上海 -> 贵州各城市")
        print("=" * 50)
        
        all_trains = []
        for city in self.guizhou_cities:
            trains = self.scrape_route("上海", city, date)
            all_trains.extend(trains)
            time.sleep(2)  # 避免请求过于频繁
        
        if all_trains:
            self.save_to_csv(all_trains, f"上海到贵州各城市_{date}.csv")
        return all_trains
    
    def run_all_scraping(self, date="2025-06-05"):
        """执行所有抓取任务"""
        print(f"开始抓取火车票信息 - 日期: {date}")
        print(f"目标贵州城市: {', '.join(self.guizhou_cities)}")
        
        try:
            # 1. 上海到贵阳
            shanghai_guiyang = self.scrape_shanghai_to_guiyang(date)
            
            # 2. 贵阳到贵州各城市
            guiyang_cities = self.scrape_guiyang_to_guizhou_cities(date)
            
            # 3. 上海到贵州各城市
            shanghai_cities = self.scrape_shanghai_to_guizhou_cities(date)
            
            # 汇总结果
            total_trains = len(shanghai_guiyang) + len(guiyang_cities) + len(shanghai_cities)
            print("=" * 50)
            print("抓取完成！")
            print(f"上海->贵阳: {len(shanghai_guiyang)} 条")
            print(f"贵阳->贵州各城市: {len(guiyang_cities)} 条")
            print(f"上海->贵州各城市: {len(shanghai_cities)} 条")
            print(f"总计: {total_trains} 条车次信息")
            print("数据保存在 train_data 文件夹中")
            print("=" * 50)
            
        except Exception as e:
            print(f"抓取过程中出现错误: {str(e)}")

def main():
    """主函数"""
    scraper = TrainTicketScraper()
    
    # 可以指定日期，默认为2025-06-05
    date = "2025-06-05"
    
    print("火车票信息抓取工具")
    print("1. 抓取所有路线")
    print("2. 仅抓取上海到贵阳")
    print("3. 仅抓取贵阳到贵州各城市")
    print("4. 仅抓取上海到贵州各城市")
    
    choice = input("请选择操作 (1-4): ").strip()
    
    if choice == "1":
        scraper.run_all_scraping(date)
    elif choice == "2":
        scraper.scrape_shanghai_to_guiyang(date)
    elif choice == "3":
        scraper.scrape_guiyang_to_guizhou_cities(date)
    elif choice == "4":
        scraper.scrape_shanghai_to_guizhou_cities(date)
    else:
        print("无效选择，执行所有抓取任务")
        scraper.run_all_scraping(date)

if __name__ == "__main__":
    main()
