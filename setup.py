# -*- coding: utf-8 -*-
"""
景点数据爬虫核心技术实现
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv
import re

def extract_attraction_info(driver):
    """核心：从页面提取景点信息"""
    attractions = []
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    # 定位景点卡片
    attraction_cards = soup.find_all("div", class_="gsl-common-card")
    
    for card in attraction_cards:
        # 多选择器策略提取名称
        name_selectors = [
            "p.title",
            ".guide-main-item-bottom .title", 
            ".content",
            "a[target='_blank']"
        ]
        
        name = "未知景点"
        for selector in name_selectors:
            name_elem = card.select_one(selector)
            if name_elem and name_elem.get_text(strip=True):
                name = name_elem.get_text(strip=True)
                break
        
        # 图片链接提取（支持多种格式）
        image_url = "无图片"
        img_selectors = [
            ".guide-main-item-top img",
            "img",
            "[style*='background-image']"
        ]
        
        for selector in img_selectors:
            if selector == "[style*='background-image']":
                # 背景图片处理
                bg_elem = card.select_one(selector)
                if bg_elem and bg_elem.get('style'):
                    url_match = re.search(r'url\(["\']?(.*?)["\']?\)', bg_elem.get('style'))
                    if url_match:
                        image_url = url_match.group(1)
                        # 相对路径转绝对路径
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        break
            else:
                # img标签处理
                img_elem = card.select_one(selector)
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src')
                    if img_src:
                        image_url = img_src
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        break
        
        # 正则表达式提取评分和评论数
        score = "暂无评分"
        review_count = "暂无评分人数"
        
        # 从tag元素提取
        tag_elem = card.find("p", class_="tag")
        if tag_elem:
            spans = tag_elem.find_all("span")
            for span in spans:
                span_text = span.get_text(strip=True)
                
                # 评分匹配
                score_match = re.match(r'^(\d+\.\d+)分?$', span_text)
                if score_match:
                    score = score_match.group(1) + "分"
                
                # 评论数匹配
                review_match = re.search(r'(\d+)(?:条评论|人评价|条点评|条评价|人点评)', span_text)
                if review_match:
                    review_count = review_match.group(0)
        
        attractions.append({
            'name': name,
            'score': score, 
            'review_count': review_count,
            'image_url': image_url
        })
    
    return attractions

def main():
    service = Service(r"chromedriver路径")
    driver = webdriver.Chrome(service=service)
    
    try:
        # 访问目标页面
        driver.get("https://you.ctrip.com/globalsearch/?keyword=%E8%B4%B5%E5%B7%9E%E6%99%AF%E7%82%B9")
        
        # 翻页核心逻辑
        all_attractions = []
        for page_num in range(1, 11):
            if page_num > 1:
                # 页码输入翻页
                page_input = driver.find_element(By.XPATH, '//input[@aria-label="页"]')
                page_input.clear()
                page_input.send_keys(str(page_num))
                page_input.send_keys(Keys.RETURN)
                time.sleep(4)
            
            # 提取当前页数据
            attractions = extract_attraction_info(driver)
            all_attractions.extend(attractions)
        
        # 保存CSV
        with open("贵州景点基本信息.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["景点名称", "评分", "评分人数", "图片链接"])
            for attraction in all_attractions:
                writer.writerow([attraction['name'], attraction['score'], 
                               attraction['review_count'], attraction['image_url']])
                
    except Exception as e:
        print(f"爬取失败: {e}")
    finally:
        driver.quit()

# ... 其他辅助函数省略 ...

if __name__ == "__main__":
    main()