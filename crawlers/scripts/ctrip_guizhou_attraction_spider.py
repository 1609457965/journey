# -*- coding: utf-8 -*-
"""Ctrip Guizhou attraction and comment Selenium crawler.

Generated from: scen.ipynb
Notebook outputs are intentionally omitted; only source code cells are kept.
"""

# %% [notebook cell 1]
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:44:00 2025
@author: Airble Dellen
整合版：爬取景点名称、评分、评分人数和详细评论信息
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
    """保存景点基本数据到CSV文件"""
    filename = "景点基本信息.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["景点名称", "评分", "评分人数"])
        for attraction in attractions_data:
            writer.writerow([attraction['name'], attraction['score'], attraction['review_count']])

def save_comment_data(name, score, user, detail, data):
    """保存评论数据到CSV文件"""
    filename = f"{name}_评论.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["评分", "用户", "评论详情", "日期", "IP位置"])
        
        # 分离日期和IP位置
        date = data[:10] if len(data) >= 10 else data
        ip_location = data[10:] if len(data) > 10 else ""
        writer.writerow([score, user, detail, date, ip_location])

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
            
            # 提取评分和评分人数
            tag_elem = card.find("p", class_="tag")
            if tag_elem:
                spans = tag_elem.find_all("span")
                
                for span in spans:
                    span_text = span.get_text(strip=True)
                    
                    # 提取评分（如：4.4分）
                    if re.match(r'^\d+\.\d+分?$', span_text) or re.match(r'^\d+\.\d+$', span_text):
                        score = span_text if span_text.endswith('分') else span_text + "分"
                    
                    # 提取评分人数
                    review_match = re.search(r'(\d+)(?:条评论|人评价|条点评|条评价|人点评)', span_text)
                    if review_match:
                        review_count = review_match.group(0)
            
            # 如果在tag中没找到，尝试在整个卡片中查找
            if score == "暂无评分" or review_count == "暂无评分人数":
                card_text = card.get_text()
                
                if score == "暂无评分":
                    score_match = re.search(r'(\d+\.\d+)分?', card_text)
                    if score_match:
                        score = score_match.group(1) + "分"
                
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

def scrape_attraction_comments(driver, attraction_name):
    """爬取单个景点的评论信息"""
    print(f"\n开始爬取 {attraction_name} 的评论...")
    
    previous_first_user = None
    comment_count = 0
    
    # 爬取前10页评论
    for page_num in range(2, 12):  # 从第2页开始，爬取10页
        try:
            time.sleep(8)
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')
            
            # 查找评论
            chats = soup.find_all("div", {"class": "commentItem"})
            if not chats:
                print("没有更多评论，结束爬取。")
                break
            
            # 检查是否到达最后一页
            current_first_user = chats[0].find("div", {"class": "userName"}).text
            if previous_first_user is not None and current_first_user == previous_first_user:
                print("到达最后一页，结束爬取。")
                break
            
            # 提取评论信息
            for chat in chats:
                try:
                    user = chat.find("div", {"class": "userName"}).text
                    detail = chat.find("div", {"class": "commentDetail"}).text
                    score = chat.find("span", {"class": "averageScore"}).text
                    data = chat.find("div", {"class": "commentTime"}).text
                    
                    save_comment_data(attraction_name, score, user, detail, data)
                    comment_count += 1
                    
                    print(f"评分: {score}, 用户: {user}")
                    
                except Exception as e:
                    print(f"提取评论时出错: {e}")
                    continue
            
            previous_first_user = current_first_user
            
            # 翻到下一页
            try:
                chatNUM = driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-options input[type='text']")
                chatNUM.clear()
                chatNUM.send_keys(str(page_num))
                chatNUM.send_keys(Keys.RETURN)
                time.sleep(2)
            except Exception as e:
                print(f"翻页失败: {e}")
                break
                
        except Exception as e:
            print(f"处理第 {page_num} 页评论时出错: {e}")
            continue
    
    print(f"{attraction_name} 评论爬取完成，共获取 {comment_count} 条评论")

def main():
    # 配置Chrome驱动路径
    service = Service(r"F:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
     
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

        # 爬取景点基本信息（前10页）
        for page_num in range(1, 11):
            print(f"\n正在爬取第 {page_num} 页景点信息...")
            
            try:
                # 翻页处理
                if page_num > 1:
                    try:
                        page_input = driver.find_element(By.XPATH, '//input[@aria-label="页"]')
                        page_input.clear()
                        page_input.send_keys(str(page_num))
                        page_input.send_keys(Keys.RETURN)
                        time.sleep(3)
                    except Exception as e:
                        print(f"翻页失败: {e}")
                        break
                
                # 提取景点信息
                attractions = extract_attraction_info(driver)
                if attractions:
                    all_attractions.extend(attractions)
                    print(f"第 {page_num} 页获取到 {len(attractions)} 个景点")
                else:
                    print(f"第 {page_num} 页未获取到景点数据")
                    if page_num > 3:
                        break
                
            except Exception as e:
                print(f"处理第 {page_num} 页时出错: {e}")
                continue

        # 保存景点基本信息
        if all_attractions:
            save_attraction_data(all_attractions)
            print(f"\n景点基本信息爬取完成！共获取到 {len(all_attractions)} 个景点")
        
        # 开始爬取每个景点的详细评论
        print("\n开始爬取景点详细评论...")
        
        # 重新定位到第一页
        driver.get("https://you.ctrip.com/globalsearch/?keyword=%E8%B4%B5%E5%B7%9E%E6%99%AF%E7%82%B9")
        time.sleep(3)
        
        gslmore = driver.find_element(By.ID, "home-page-travel-list").find_element(By.CLASS_NAME, "gsl-more")
        actions = ActionChains(driver)
        actions.click(gslmore)
        actions.perform()
        time.sleep(3)
        
        # 逐页爬取评论
        for page_num in range(1, 11):
            try:
                # 翻页
                if page_num > 1:
                    page_input = driver.find_element(By.XPATH, '//input[@aria-label="页"]')
                    page_input.clear()
                    page_input.send_keys(str(page_num))
                    page_input.send_keys(Keys.RETURN)
                    time.sleep(3)
                
                # 获取当前页面的景点卡片
                view = driver.find_element(By.ID, "home-page-travel-list").find_elements(By.CLASS_NAME, "gsl-common-card")
                
                # 修正景点选择逻辑：第一页从第一个景点开始，不跳过任何景点
                start_index = 0  # 从第一个景点开始
                
                print(f"第 {page_num} 页共找到 {len(view)} 个景点卡片")
                
                for i, attraction_card in enumerate(view[start_index:], start=start_index):
                    try:
                        print(f"正在处理第 {i+1} 个景点...")
                        
                        # 点击景点卡片
                        actions = ActionChains(driver)
                        actions.click(attraction_card)
                        actions.perform()
                        time.sleep(2)
                        
                        # 切换到新窗口
                        windows = driver.window_handles
                        if len(windows) > 1:
                            driver.switch_to.window(windows[1])
                            
                            # 获取景点名称
                            html_source = driver.page_source
                            soup = BeautifulSoup(html_source, 'lxml')
                            name_elem = soup.find("div", {"class": "title"})
                            if name_elem and name_elem.find("h1"):
                                attraction_name = name_elem.find("h1").text
                                print(f"开始爬取景点：{attraction_name}")
                                
                                # 爬取该景点的评论
                                scrape_attraction_comments(driver, attraction_name)
                            
                            # 关闭当前窗口，回到主窗口
                            driver.close()
                            driver.switch_to.window(windows[0])
                        else:
                            print("未能打开新窗口，跳过此景点")
                        
                    except Exception as e:
                        print(f"处理第 {i+1} 个景点时出错: {e}")
                        # 确保回到主窗口
                        windows = driver.window_handles
                        if len(windows) > 1:
                            driver.close()
                        if windows:
                            driver.switch_to.window(windows[0])
                        continue
                        
            except Exception as e:
                print(f"处理第 {page_num} 页评论时出错: {e}")
                continue

        print("\n所有数据爬取完成！")
        print("景点基本信息已保存到 '景点基本信息.csv'")
        print("各景点评论已分别保存到对应的CSV文件")

    except Exception as e:
        print(f"程序执行出错: {e}")

    finally:
        driver.quit()
        print("浏览器已关闭")

# 运行主程序
if __name__ == "__main__":
    main()

# %% [notebook cell 2]
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:44:00 2025
@author: Airble Dellen
专门爬取景点基本信息：名称、评分、评分人数、图片链接
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains 
import time
from bs4 import BeautifulSoup
import csv
import re

def save_attraction_data(attractions_data):
    """保存景点基本数据到CSV文件"""
    filename = "贵州景点基本信息.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["景点名称", "评分", "评分人数", "图片链接"])
        for attraction in attractions_data:
            writer.writerow([
                attraction['name'], 
                attraction['score'], 
                attraction['review_count'],
                attraction['image_url']
            ])

def extract_attraction_info(driver):
    """从当前页面提取景点信息"""
    attractions = []
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    # 查找所有景点卡片
    attraction_cards = soup.find_all("div", class_="gsl-common-card")
    
    print(f"本页找到 {len(attraction_cards)} 个景点卡片")
    
    for i, card in enumerate(attraction_cards, 1):
        try:
            print(f"正在处理第 {i} 个景点...")
            
            # 提取景点名称
            name = "未知景点"
            # 尝试多种可能的名称选择器
            name_selectors = [
                "p.title",
                ".guide-main-item-bottom .title",
                ".content",
                "a[target='_blank']"
            ]
            
            for selector in name_selectors:
                name_elem = card.select_one(selector)
                if name_elem:
                    name_text = name_elem.get_text(strip=True)
                    if name_text and len(name_text) > 0:
                        name = name_text
                        break
            
            # 如果仍然没有找到名称，尝试从链接的title属性获取
            if name == "未知景点":
                link_elem = card.find("a", target="_blank")
                if link_elem and link_elem.get('title'):
                    name = link_elem.get('title').strip()
            
            # 提取图片链接
            image_url = "无图片"
            # 查找图片元素
            img_selectors = [
                ".guide-main-item-top img",
                "img",
                "[style*='background-image']"
            ]
            
            for selector in img_selectors:
                if selector == "[style*='background-image']":
                    # 处理背景图片
                    bg_elem = card.select_one(selector)
                    if bg_elem and bg_elem.get('style'):
                        style = bg_elem.get('style')
                        url_match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                        if url_match:
                            image_url = url_match.group(1)
                            # 如果是相对路径，补全为绝对路径
                            if image_url.startswith('//'):
                                image_url = 'https:' + image_url
                            elif image_url.startswith('/'):
                                image_url = 'https://you.ctrip.com' + image_url
                            break
                else:
                    # 处理img标签
                    img_elem = card.select_one(selector)
                    if img_elem:
                        img_src = img_elem.get('src') or img_elem.get('data-src')
                        if img_src:
                            image_url = img_src
                            # 如果是相对路径，补全为绝对路径
                            if image_url.startswith('//'):
                                image_url = 'https:' + image_url
                            elif image_url.startswith('/'):
                                image_url = 'https://you.ctrip.com' + image_url
                            break
            
            # 初始化评分和评分人数
            score = "暂无评分"
            review_count = "暂无评分人数"
            
            # 提取评分和评分人数
            # 方法1：从tag元素中提取
            tag_elem = card.find("p", class_="tag")
            if tag_elem:
                spans = tag_elem.find_all("span")
                for span in spans:
                    span_text = span.get_text(strip=True)
                    
                    # 提取评分（如：4.4分、4.4）
                    score_match = re.match(r'^(\d+\.\d+)分?$', span_text)
                    if score_match:
                        score = score_match.group(1) + "分"
                    
                    # 提取评分人数
                    review_match = re.search(r'(\d+)(?:条评论|人评价|条点评|条评价|人点评)', span_text)
                    if review_match:
                        review_count = review_match.group(0)
            
            # 方法2：如果在tag中没找到，尝试在整个卡片中查找
            if score == "暂无评分" or review_count == "暂无评分人数":
                card_text = card.get_text()
                
                # 查找评分
                if score == "暂无评分":
                    score_patterns = [
                        r'(\d+\.\d+)分',
                        r'评分[：:]\s*(\d+\.\d+)',
                        r'(\d+\.\d+)/5',
                        r'(\d+\.\d+)★'
                    ]
                    for pattern in score_patterns:
                        score_match = re.search(pattern, card_text)
                        if score_match:
                            score = score_match.group(1) + "分"
                            break
                
                # 查找评分人数
                if review_count == "暂无评分人数":
                    review_patterns = [
                        r'(\d+条评论)',
                        r'(\d+人评价)',
                        r'(\d+条点评)',
                        r'(\d+条评价)',
                        r'(\d+人点评)',
                        r'(\d+)\s*人评价',
                        r'(\d+)\s*条评论'
                    ]
                    for pattern in review_patterns:
                        review_match = re.search(pattern, card_text)
                        if review_match:
                            review_count = review_match.group(0)
                            break
            
            # 创建景点信息字典
            attraction_info = {
                'name': name,
                'score': score,
                'review_count': review_count,
                'image_url': image_url
            }
            
            attractions.append(attraction_info)
            
            print(f"景点: {name}")
            print(f"评分: {score}")
            print(f"评分人数: {review_count}")
            print(f"图片链接: {image_url[:50]}..." if len(image_url) > 50 else f"图片链接: {image_url}")
            print("-" * 50)
            
        except Exception as e:
            print(f"提取第 {i} 个景点信息时出错: {e}")
            continue
    
    return attractions

def main():
    # 配置Chrome驱动路径 - 请根据您的实际路径修改
    service = Service(r"F:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
        # 访问贵州景点搜索页面
        driver.get("https://you.ctrip.com/globalsearch/?keyword=%E8%B4%B5%E5%B7%9E%E6%99%AF%E7%82%B9")
        print("页面标题:", driver.title)
        time.sleep(5)  # 增加等待时间，确保页面完全加载

        # 点击"更多"按钮展开更多景点
        try:
            # 等待页面加载完成
            time.sleep(3)
            gslmore = driver.find_element(By.ID, "home-page-travel-list").find_element(By.CLASS_NAME, "gsl-more")
            actions = ActionChains(driver)
            actions.click(gslmore)
            actions.perform()
            time.sleep(3)
            print("成功点击了更多按钮")
        except Exception as e:
            print(f"点击更多按钮失败: {e}")
            print("尝试继续执行...")

        all_attractions = []

        # 爬取前10页景点基本信息
        for page_num in range(1, 11):
            print(f"\n{'='*60}")
            print(f"正在爬取第 {page_num} 页景点信息...")
            print(f"{'='*60}")
            
            try:
                # 翻页处理（第一页不需要翻页）
                if page_num > 1:
                    try:
                        # 查找页码输入框
                        page_input = driver.find_element(By.XPATH, '//input[@aria-label="页"]')
                        page_input.clear()
                        page_input.send_keys(str(page_num))
                        page_input.send_keys(Keys.RETURN)
                        time.sleep(4)  # 等待页面加载
                        print(f"成功翻到第 {page_num} 页")
                    except Exception as e:
                        print(f"翻页到第 {page_num} 页失败: {e}")
                        # 尝试其他翻页方法
                        try:
                            next_button = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')] | //button[contains(text(), '下一页')]")
                            next_button.click()
                            time.sleep(4)
                        except:
                            print(f"无法翻到第 {page_num} 页，停止爬取")
                            break
                
                # 提取当前页面的景点信息
                attractions = extract_attraction_info(driver)
                
                if attractions:
                    all_attractions.extend(attractions)
                    print(f"第 {page_num} 页成功获取到 {len(attractions)} 个景点信息")
                else:
                    print(f"第 {page_num} 页未获取到景点数据")
                    # 如果连续几页都没有数据，可能已到末尾
                    if page_num > 3:
                        print("可能已经到达最后一页，停止爬取")
                        break
                
            except Exception as e:
                print(f"处理第 {page_num} 页时出错: {e}")
                continue

        # 保存所有数据
        if all_attractions:
            save_attraction_data(all_attractions)
            print(f"\n{'='*60}")
            print(f"爬取完成！")
            print(f"共获取到 {len(all_attractions)} 个景点的基本信息")
            print(f"数据已保存到 '贵州景点基本信息.csv' 文件")
            print(f"{'='*60}")
            
            # 显示统计信息
            print("\n统计信息:")
            print(f"有评分的景点: {len([a for a in all_attractions if a['score'] != '暂无评分'])} 个")
            print(f"有评分人数的景点: {len([a for a in all_attractions if a['review_count'] != '暂无评分人数'])} 个")
            print(f"有图片的景点: {len([a for a in all_attractions if a['image_url'] != '无图片'])} 个")
            
        else:
            print("未获取到任何景点数据，请检查:")
            print("1. 网络连接是否正常")
            print("2. Chrome驱动路径是否正确")
            print("3. 页面结构是否发生变化")

    except Exception as e:
        print(f"程序执行出错: {e}")

    finally:
        driver.quit()
        print("\n浏览器已关闭")

# 运行主程序
if __name__ == "__main__":
    main()
