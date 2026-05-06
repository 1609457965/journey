# -*- coding: utf-8 -*-
"""Douban Top250 books requests/BeautifulSoup crawler.

Generated from: mp4_totext.ipynb
Notebook outputs are intentionally omitted; only source code cells are kept.
"""

# %% [notebook cell 2]
import requests
from bs4 import BeautifulSoup
import time
import json

# 请求头设置
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 存储所有书籍数据
books_data = []

def fetch_books():
    # 生成10页URL（每页25条）
    for start in range(0, 250, 25):
        url = f'https://book.douban.com/top250?start={start}'
        print(f'正在爬取：{url}')
        
        # 发送请求
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取每本书
        for item in soup.select('tr.item'):
            # 书名（使用 title 属性避免副标题干扰）
            title = item.select_one('.pl2 a')['title'].strip()
            
            # 作者信息（从 p.pl 中分割）
            info = item.select_one('p.pl').text.strip()
            author = info.split('/')[0].strip() if info else ''
            
            # 评分
            rating = item.select_one('.rating_nums').text.strip()
            
            # 评分人数（正则提取数字）
            rating_people = item.select_one('.star .pl').text.strip()
            rating_people = ''.join(filter(str.isdigit, rating_people))
            
            # 简介（可能不存在）
            summary_tag = item.select_one('.inq')
            summary = summary_tag.text.strip() if summary_tag else ''
            
            # 保存数据
            books_data.append({
                '书名': title,
                '作者': author,
                '评分': rating,
                '评分人数': rating_people,
                '简介': summary
            })
        
        # 遵守豆瓣反爬，延迟2秒
        time.sleep(2)

if __name__ == '__main__':
    fetch_books()
    # 保存为JSON
    with open('books.json', 'w', encoding='utf-8') as f:
        json.dump(books_data, f, ensure_ascii=False, indent=2)
    print('数据已保存到 books.json')
