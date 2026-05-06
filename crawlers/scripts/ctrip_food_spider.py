# -*- coding: utf-8 -*-
"""Ctrip Guizhou food and restaurant-comment Selenium crawler.

Generated from: foodmark.ipynb
Notebook outputs are intentionally omitted; only source code cells are kept.
"""

# %% [notebook cell 1]
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:44:00 2025

@author: Airble Dellen
爬取贵州美食的名称、评分和评论个数 - 通过点击美食分类
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv
import os
import re

def save_food_data(foods_data):
    """保存美食数据到CSV文件"""
    filename = "贵州美食评分.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["美食名称", "评分", "评论个数"])
        for food in foods_data:
            writer.writerow([food['name'], food['score'], food['comments']])

def extract_food_info(driver):
    """从当前页面提取美食信息"""
    foods = []
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    # 根据提供的HTML结构查找美食卡片 - 查找gsl-common-card
    food_cards = soup.find_all("div", class_="gsl-common-card")
    
    for card in food_cards:
        try:
            # 提取美食名称 - 根据HTML结构查找title类的p标签
            name_elem = card.find("p", class_="title")
            if name_elem:
                name = name_elem.get_text(strip=True)
            else:
                continue
            
            # 提取评分和评论个数
            score = "暂无评分"
            comments = "暂无评论"
            
            # 查找tag类的p标签，里面包含评分和评论信息
            tag_elem = card.find("p", class_="tag")
            if tag_elem:
                # 查找span标签，根据HTML结构，评分在span中
                spans = tag_elem.find_all("span")
                for span in spans:
                    span_text = span.get_text(strip=True)
                    
                    # 提取评分（如：4.4）
                    if re.match(r'^\d+\.\d+$', span_text):
                        score = span_text + "分"
                    
                    # 提取评论个数（如：472条评论）
                    comment_match = re.search(r'(\d+)条评[论价]', span_text)
                    if comment_match:
                        comments = comment_match.group(0)
            
            # 如果在tag中没找到，尝试在整个卡片中查找
            if score == "暂无评分" or comments == "暂无评论":
                card_text = card.get_text()
                
                # 查找评分
                if score == "暂无评分":
                    score_match = re.search(r'(\d+\.\d+)', card_text)
                    if score_match:
                        score = score_match.group(1) + "分"
                
                # 查找评论数
                if comments == "暂无评论":
                    comment_match = re.search(r'(\d+)条评[论价]', card_text)
                    if comment_match:
                        comments = comment_match.group(0)
            
            foods.append({
                'name': name,
                'score': score,
                'comments': comments
            })
            
            print(f"美食: {name}, 评分: {score}, 评论: {comments}")
            
        except Exception as e:
            print(f"提取美食信息时出错: {e}")
            continue
    
    return foods

# 主程序
def main():
    service = Service(r"F:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    try:
        # 访问贵州搜索页面
        driver.get("https://you.ctrip.com/globalsearch/?keyword=%E8%B4%B5%E5%B7%9E")
        print("页面标题:", driver.title)
        time.sleep(3)

        # 查找并点击美食分类按钮
        try:
            # 等待页面加载完成
            time.sleep(5)
            
            print("正在查找美食分类按钮...")
            
            # 根据HTML结构，美食按钮在entry-container中的entry-item里
            food_button_selectors = [
                "//div[@class='entry-container']//div[@class='entry-item' and contains(text(), '美食')]",
                "//div[@class='entry-item']//div[@class='entry-item-text-hight' and text()='美食']",
                "//div[@class='entry-item'][contains(., '美食')]",
                "//div[contains(@class, 'entry-item') and contains(text(), '美食')]",
                "//*[@class='entry-item-text-hight' and text()='美食']",
                "//*[contains(@class, 'entry') and text()='美食']",
                "//span[text()='美食']",
                "//a[text()='美食']", 
                "//div[text()='美食']",
                "//li[text()='美食']",
                "//*[@class='tab-item' and contains(text(), '美食')]",
                "//*[contains(@class, 'category-item') and text()='美食']",
                "//*[contains(@class, 'filter') and text()='美食']",
                "//*[contains(@class, 'nav') and text()='美食']"
            ]
            
            food_button = None
            for selector in food_button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        food_button = elements[0]
                        print(f"找到美食按钮: {selector}")
                        break
                except Exception as e:
                    print(f"尝试选择器 {selector} 失败: {e}")
                    continue
            
            # 如果上面的方法没找到，尝试查找所有entry-item中包含美食的元素
            if not food_button:
                print("尝试查找所有entry-item中的美食元素...")
                try:
                    # 查找所有entry-item元素
                    entry_items = driver.find_elements(By.CLASS_NAME, "entry-item")
                    print(f"找到 {len(entry_items)} 个entry-item元素")
                    
                    for item in entry_items:
                        try:
                            item_text = item.text.strip()
                            print(f"entry-item文本: '{item_text}'")
                            if '美食' in item_text:
                                food_button = item
                                print(f"找到包含美食的entry-item: {item_text}")
                                break
                        except Exception as e:
                            print(f"读取entry-item文本失败: {e}")
                            continue
                except Exception as e:
                    print(f"查找entry-item元素时出错: {e}")
            
            # 如果还是没找到，尝试查找所有分类按钮
            if not food_button:
                print("尝试查找所有分类按钮...")
                try:
                    # 查找所有可能包含分类的元素
                    category_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'tab') or contains(@class, 'category') or contains(@class, 'filter') or contains(@class, 'nav')]")
                    for elem in category_elements:
                        if elem.text and '美食' in elem.text:
                            food_button = elem
                            print(f"找到美食分类: {elem.text}")
                            break
                except Exception as e:
                    print(f"查找分类元素时出错: {e}")
            
            # 如果还是没找到，打印所有可能的分类元素
            if not food_button:
                print("未找到美食按钮，打印页面上所有分类相关元素...")
                try:
                    # 查找所有可能包含分类的元素
                    all_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'entry') or contains(text(), '美食') or contains(text(), '餐厅')]")
                    for elem in all_elements:
                        try:
                            elem_text = elem.text.strip()
                            if elem_text:
                                print(f"找到元素: '{elem_text}' - 标签: {elem.tag_name} - 类名: {elem.get_attribute('class')}")
                        except:
                            pass
                except Exception as e:
                    print(f"打印调试信息时出错: {e}")
            
            if food_button:
                print(f"正在点击美食按钮...")
                # 滚动到元素可见位置
                driver.execute_script("arguments[0].scrollIntoView(true);", food_button)
                time.sleep(1)
                # 点击按钮
                driver.execute_script("arguments[0].click();", food_button)
                time.sleep(5)
                print("美食按钮点击成功！")
            else:
                print("未找到美食按钮，将继续尝试爬取当前页面数据...")
                
        except Exception as e:
            print(f"点击美食按钮失败: {e}")

        # 等待美食列表加载
        time.sleep(3)

        # 点击"更多"按钮展开更多美食（如果存在）
        try:
            more_button = driver.find_element(By.CLASS_NAME, "gsl-more")
            actions = ActionChains(driver)
            actions.click(more_button)
            actions.perform()
            time.sleep(3)
            print("点击了更多按钮")
        except Exception as e:
            print(f"点击更多按钮失败或不存在: {e}")

        all_foods = []

        # 爬取多页数据
        for page_num in range(1, 11):
            print(f"\n正在爬取第 {page_num} 页...")
            
            try:
                # 如果不是第一页，需要翻页
                if page_num > 1:
                    try:
                        # 查找页码输入框
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
                
                # 提取当前页面的美食信息
                foods = extract_food_info(driver)
                if foods:
                    all_foods.extend(foods)
                    print(f"第 {page_num} 页获取到 {len(foods)} 个美食")
                else:
                    print(f"第 {page_num} 页未获取到美食数据")
                    # 如果连续几页都没有数据，可能已到末尾
                    if page_num > 3:
                        break
                
            except Exception as e:
                print(f"处理第 {page_num} 页时出错: {e}")
                continue

        # 保存所有数据
        if all_foods:
            save_food_data(all_foods)
            print(f"\n爬取完成！共获取到 {len(all_foods)} 个美食信息")
            print("数据已保存到 '贵州美食评分.csv' 文件")
        else:
            print("未获取到任何美食数据，请检查页面结构或网络连接")

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
携程美食爬虫：爬取美食名称、地点、人均、点评数、评分和详细评论信息
修复版本 - 修复美食名称提取问题并实现实时写入
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from bs4 import BeautifulSoup
import csv
import os
import re

def init_restaurant_csv():
    """初始化美食基本信息CSV文件"""
    filename = "美食基本信息.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["美食名称", "地点", "人均消费", "点评数", "列表页评分", "详情页评分"])
    return filename

def append_restaurant_data(restaurant_data, filename):
    """实时追加美食基本数据到CSV文件"""
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        detailed_score = restaurant_data.get('detailed_score', '未获取')
        writer.writerow([restaurant_data['name'], restaurant_data['location'], 
                       restaurant_data['price'], restaurant_data['review_count'], 
                       restaurant_data['score'], detailed_score])
    print(f"已保存: {restaurant_data['name']}")

def save_comment_data(name, score, user, detail, data):
    """保存评论数据到CSV文件"""
    # 清理文件名中的特殊字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    filename = f"{safe_name}_评论.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["评分", "用户", "评论详情", "日期", "IP位置"])
        
        # 分离日期和IP位置
        date = data[:10] if len(data) >= 10 else data
        ip_location = data[10:] if len(data) > 10 else ""
        writer.writerow([score, user, detail, date, ip_location])

def extract_restaurant_info(driver):
    """从当前页面提取美食信息 - 修复版本"""
    restaurants = []
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    # 查找所有美食卡片
    restaurant_cards = soup.find_all("div", class_="list_mod2")
    
    for card in restaurant_cards:
        try:
            # 修复：根据HTML结构提取美食名称
            name = "未知美食"
            
            # 方法1：从target="_blank"的链接title属性获取
            name_link = card.find("a", {"target": "_blank"})
            if name_link and name_link.get('title'):
                # title格式可能是："黔渝苗家风味馆(喀水冲店)→苗家土菜(喀水冲店)"
                title_text = name_link.get('title').strip()
                if '→' in title_text:
                    # 取→后面的名称，通常更准确
                    name = title_text.split('→')[-1].strip()
                else:
                    name = title_text
            
            # 方法2：如果没有title，尝试从href中提取
            if name == "未知美食" and name_link and name_link.get('href'):
                href = name_link.get('href')
                # href可能包含美食ID，可以作为备用
                import re
                match = re.search(r'/(\d+)\.html', href)
                if match:
                    name = f"美食_{match.group(1)}"
            
            # 方法3：从i.restaurant元素获取
            if name == "未知美食":
                name_elem = card.find("i", class_="restaurant")
                if name_elem:
                    name = name_elem.get_text(strip=True)
            
            # 方法4：从dt元素获取
            if name == "未知美食":
                dt_elem = card.find("dt")
                if dt_elem:
                    # 排除价格和评分信息
                    dt_text = dt_elem.get_text(strip=True)
                    # 移除可能的价格和评分信息
                    clean_text = re.sub(r'￥\d+|人均.*|条点评.*|\d+\.\d+', '', dt_text).strip()
                    if clean_text and len(clean_text) > 2:
                        name = clean_text
            
            # 方法5：尝试从链接文本获取（去除HTML标签后）
            if name == "未知美食" and name_link:
                link_text = name_link.get_text(strip=True)
                # 清理可能的多余信息
                clean_link_text = re.sub(r'￥\d+.*|人均.*|条点评.*', '', link_text).strip()
                if clean_link_text and len(clean_link_text) > 2:
                    name = clean_link_text
            
            # 提取地点信息 - 改进版本
            location = "暂无地点信息"
            # 查找包含地址信息的dd元素
            location_elem = card.find("dd", class_="ellipsis")
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                if location_text and location_text != name:  # 确保不是重复的名称
                    location = location_text
            
            # 如果没找到，尝试其他位置
            if location == "暂无地点信息":
                dd_elements = card.find_all("dd")
                for dd in dd_elements:
                    dd_text = dd.get_text(strip=True)
                    if dd_text and "区" in dd_text or "路" in dd_text or "街" in dd_text:
                        location = dd_text
                        break
            
            # 提取人均消费
            price = "暂无价格信息"
            price_elem = card.find("span", class_="price")
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # 提取价格数字
                price_match = re.search(r'￥\s*(\d+)', price_text)
                if price_match:
                    price = f"￥{price_match.group(1)}"
                else:
                    price = price_text
            
            # 提取点评数
            review_count = "暂无点评"
            review_elem = card.find("a", class_="recomment")
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                # 提取点评数字
                review_match = re.search(r'(\d+)条点评', review_text)
                if review_match:
                    review_count = f"{review_match.group(1)}条点评"
                else:
                    review_count = review_text
            
            # 提取评分
            score = "暂无评分"
            score_elem = card.find("span", class_="score")
            if score_elem:
                score_text = score_elem.get_text(strip=True)
                score = score_text
            
            restaurant_data = {
                'name': name,
                'location': location,
                'price': price,
                'review_count': review_count,
                'score': score
            }
            
            restaurants.append(restaurant_data)
            
            print(f"美食: {name}, 地点: {location}, 人均: {price}, 点评数: {review_count}, 评分: {score}")
            
        except Exception as e:
            print(f"提取美食信息时出错: {e}")
            continue
    
    return restaurants

def extract_detailed_score(driver):
    """提取美食详情页的详细评分"""
    try:
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        # 根据你提供的HTML结构，查找detailtop_r_info中的评分
        detail_info = soup.find("ul", class_="detailtop_r_info")
        if detail_info:
            # 查找第一个li元素
            score_li = detail_info.find("li")
            if score_li:
                # 查找span.score元素
                score_span = score_li.find("span", class_="score")
                if score_span:
                    # 查找b标签中的评分数字
                    score_b = score_span.find("b")
                    if score_b:
                        score_text = score_b.get_text(strip=True)
                        return score_text
        
        # 备用方案：直接查找span.score
        score_elem = soup.find("span", class_="score")
        if score_elem:
            # 查找b标签
            score_b = score_elem.find("b")
            if score_b:
                return score_b.get_text(strip=True)
            else:
                # 如果没有b标签，直接返回span的文本
                detailed_score = score_elem.get_text(strip=True)
                return detailed_score
        
        # 尝试查找包含数字评分的b标签
        score_elem = soup.find("b", string=re.compile(r'\d+\.\d+'))
        if score_elem:
            return score_elem.get_text(strip=True)
            
        return "暂无详细评分"
        
    except Exception as e:
        print(f"提取详细评分时出错: {e}")
        return "暂无详细评分"

def scrape_restaurant_comments(driver, restaurant_name, max_pages=10):
    """爬取单个美食的评论信息"""
    print(f"\n开始爬取 {restaurant_name} 的评论...")
    
    previous_first_user = None
    comment_count = 0
    
    # 爬取前10页评论
    for page_num in range(1, max_pages + 1):
        try:
            time.sleep(3)
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')
            
            # 根据新的HTML结构查找评论
            # 查找评论容器
            comment_box = soup.find("div", {"id": "sightcommentbox"})
            if comment_box:
                # 查找所有评论项
                chats = comment_box.find_all("div", {"class": "comment_single"})
            else:
                # 备用选择器
                chats = soup.find_all("div", {"class": "comment_single"})
            
            if not chats:
                print("没有更多评论，结束爬取。")
                break
            
            # 检查是否到达最后一页
            if len(chats) > 0:
                first_comment = chats[0]
                current_first_user = None
                
                # 获取用户名 - 根据新结构调整
                usering_elem = first_comment.find("div", {"class": "usering"})
                if usering_elem:
                    user_link = usering_elem.find("a")
                    if user_link:
                        current_first_user = user_link.get_text(strip=True)
                
                if previous_first_user is not None and current_first_user == previous_first_user:
                    print("到达最后一页，结束爬取。")
                    break
                
                previous_first_user = current_first_user
            
            # 提取评论信息
            for chat in chats:
                try:
                    # 提取用户名
                    user = "匿名用户"
                    usering_elem = chat.find("div", {"class": "usering"})
                    if usering_elem:
                        user_link = usering_elem.find("a")
                        if user_link:
                            user = user_link.get_text(strip=True)
                        else:
                            # 尝试从span.ellipsis获取
                            ellipsis_span = usering_elem.find("span", {"class": "ellipsis"})
                            if ellipsis_span:
                                user_link = ellipsis_span.find("a")
                                if user_link:
                                    user = user_link.get_text(strip=True)
                    
                    # 提取评论内容
                    detail = "无评论内容"
                    main_con = chat.find("li", {"class": "main_con"})
                    if main_con:
                        heightbox = main_con.find("span", {"class": "heightbox"})
                        if heightbox:
                            # 获取评论文本，移除HTML标签
                            detail_text = heightbox.get_text(strip=True)
                            if detail_text:
                                detail = detail_text
                    
                    # 提取评分 - 从title_cf或其他位置
                    score = "无评分"
                    title_cf = chat.find("li", {"class": "title_cf"})
                    if title_cf:
                        # 尝试从星级或评分元素中获取评分
                        score_text = title_cf.get_text(strip=True)
                        if score_text:
                            score = score_text
                    
                    # 提取时间和位置信息
                    data = "无时间信息"
                    # 尝试从commenttoggle或其他位置获取时间
                    toggle_elem = chat.find("p", {"class": "commenttoggle"})
                    if toggle_elem:
                        data = toggle_elem.get_text(strip=True)
                    
                    # 只保存有内容的评论
                    if detail != "无评论内容" and len(detail.strip()) > 5:  # 至少5个字符
                        save_comment_data(restaurant_name, score, user, detail, data)
                        comment_count += 1
                        print(f"评分: {score}, 用户: {user[:10]}...")  # 只显示用户名前10个字符
                    
                except Exception as e:
                    print(f"提取单条评论时出错: {e}")
                    continue
            
            # 翻到下一页
            if page_num < max_pages:
                try:
                    # 查找下一页按钮
                    next_button = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')] | //a[contains(@class, 'next')] | //a[@class='cf' and contains(@href, 'p')]")
                    if next_button.is_enabled():
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                    else:
                        print("已到最后一页")
                        break
                except Exception as e:
                    # 尝试页码输入方式
                    try:
                        page_input = driver.find_element(By.XPATH, "//input[@type='text'] | //input[contains(@class, 'page')]")
                        page_input.clear()
                        page_input.send_keys(str(page_num + 1))
                        page_input.send_keys(Keys.RETURN)
                        time.sleep(3)
                    except Exception as e2:
                        print(f"翻页失败，尝试直接构造URL: {e2}")
                        # 尝试直接构造下一页URL
                        try:
                            current_url = driver.current_url
                            if 'p' in current_url:
                                # 替换页码
                                next_url = re.sub(r'p\d+', f'p{page_num + 1}', current_url)
                            else:
                                # 添加页码参数
                                next_url = current_url + f'&p={page_num + 1}'
                            driver.get(next_url)
                            time.sleep(3)
                        except Exception as e3:
                            print(f"构造URL失败: {e3}")
                            break
                        
        except Exception as e:
            print(f"处理第 {page_num} 页评论时出错: {e}")
            continue
    
    print(f"{restaurant_name} 评论爬取完成，共获取 {comment_count} 条评论")

def debug_html_structure(driver, save_to_file=True):
    """调试：保存当前页面HTML结构到文件"""
    try:
        html_source = driver.page_source
        if save_to_file:
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(html_source)
            print("页面HTML已保存到 debug_page_source.html")
        
        # 分析美食卡片结构
        soup = BeautifulSoup(html_source, 'lxml')
        restaurant_cards = soup.find_all("div", class_="list_mod2")
        
        if restaurant_cards:
            print(f"\n找到 {len(restaurant_cards)} 个美食卡片")
            # 分析第一个卡片的结构
            first_card = restaurant_cards[0]
            print("\n第一个美食卡片的HTML结构：")
            print("=" * 50)
            print(first_card.prettify()[:1000])  # 只显示前1000个字符
            print("=" * 50)
            
            # 查找所有可能包含名称的元素
            print("\n查找可能的名称元素：")
            name_candidates = []
            
            # 查找所有链接
            links = first_card.find_all("a")
            for j, link in enumerate(links):
                print(f"链接{j}: href={link.get('href', 'None')}, title={link.get('title', 'None')}, text='{link.get_text(strip=True)[:50]}'")
                name_candidates.append(link.get_text(strip=True))
            
            # 查找所有dt元素
            dts = first_card.find_all("dt")
            for j, dt in enumerate(dts):
                print(f"dt{j}: '{dt.get_text(strip=True)[:50]}'")
                name_candidates.append(dt.get_text(strip=True))
            
            # 查找所有i元素
            i_elements = first_card.find_all("i")
            for j, i_elem in enumerate(i_elements):
                print(f"i{j}: class={i_elem.get('class', 'None')}, text='{i_elem.get_text(strip=True)[:50]}'")
                name_candidates.append(i_elem.get_text(strip=True))
            
            print(f"\n所有候选名称: {[name[:30] for name in name_candidates if name.strip()]}")
        else:
            print("未找到美食卡片!")
            
    except Exception as e:
        print(f"调试HTML结构时出错: {e}")

def main():
    # 配置Chrome驱动路径
    service = Service(r"F:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    
    # 配置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        # 初始化CSV文件
        csv_filename = init_restaurant_csv()
        
        # 访问美食列表页面
        url = "https://you.ctrip.com/restaurantlist/Guizhou100064/list-c4914-p1.html?ordertype=0"
        driver.get(url)
        print("页面标题:", driver.title)
        time.sleep(5)

        # 添加调试功能
        print("\n=== 调试模式：分析页面结构 ===")
        debug_html_structure(driver)
        
        # 询问是否继续
        print("\n请检查debug_page_source.html文件和上面的结构分析")
        print("如果需要继续爬取，请修改extract_restaurant_info函数中的选择器")
        
        processed_count = 0

        # 爬取前10页美食信息和评论（实时处理）
        for page_num in range(1, 11):  # 改为10页，边爬边处理
            print(f"\n正在处理第 {page_num} 页...")
            
            try:
                # 等待页面加载
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list_mod2")))
                
                # 提取美食信息
                restaurants = extract_restaurant_info(driver)
                if not restaurants:
                    print(f"第 {page_num} 页未获取到美食数据")
                    continue
                
                print(f"第 {page_num} 页获取到 {len(restaurants)} 个美食")
                
                # 获取当前页面的美食卡片元素（用于点击）
                restaurant_cards = driver.find_elements(By.CLASS_NAME, "list_mod2")
                
                # 逐个处理每个美食
                for i, restaurant_info in enumerate(restaurants):
                    try:
                        print(f"\n正在处理: {restaurant_info['name']} ({i+1}/{len(restaurants)})")
                        
                        # 重新获取当前页面的美食卡片（防止页面元素失效）
                        current_cards = driver.find_elements(By.CLASS_NAME, "list_mod2")
                        if i >= len(current_cards):
                            print(f"无法找到第{i+1}个美食卡片，跳过")
                            append_restaurant_data(restaurant_info, csv_filename)
                            continue
                        
                        restaurant_card = current_cards[i]
                        
                        # 获取美食详情页链接
                        try:
                            detail_link = restaurant_card.find_element(By.CSS_SELECTOR, "a[target='_blank']")
                            detail_url = detail_link.get_attribute('href')
                            
                            if detail_url:
                                print(f"访问详情页: {detail_url}")
                                # 在新标签页中打开详情页
                                driver.execute_script("window.open(arguments[0]);", detail_url)
                                time.sleep(2)
                                
                                # 切换到新标签页
                                driver.switch_to.window(driver.window_handles[-1])
                                time.sleep(3)
                                
                                # 获取详细评分
                                detailed_score = extract_detailed_score(driver)
                                restaurant_info['detailed_score'] = detailed_score
                                print(f"详细评分：{detailed_score}")
                                
                                # 爬取该美食的评论
                                scrape_restaurant_comments(driver, restaurant_info['name'], max_pages=5)  # 减少页数提高效率
                                
                                # 关闭当前标签页，回到主页面
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                                time.sleep(1)
                            else:
                                print("未找到详情页链接")
                                
                        except Exception as link_error:
                            print(f"处理详情页链接时出错: {link_error}")
                        
                        # 实时保存美食基本信息
                        append_restaurant_data(restaurant_info, csv_filename)
                        processed_count += 1
                        print(f"已处理 {processed_count} 个美食")
                        
                    except Exception as e:
                        print(f"处理美食 {restaurant_info.get('name', '未知')} 时出错: {e}")
                        # 确保回到主标签页
                        try:
                            if len(driver.window_handles) > 1:
                                driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                        # 仍然保存基本信息
                        try:
                            append_restaurant_data(restaurant_info, csv_filename)
                        except:
                            pass
                        continue
                
                # 翻到下一页
                if page_num < 10:
                    try:
                        next_button = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')] | //a[contains(@class, 'next')]")
                        if next_button.is_enabled():
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(3)
                        else:
                            print("已到最后一页，停止爬取")
                            break
                    except NoSuchElementException:
                        print("未找到下一页按钮，停止爬取")
                        break
                    except Exception as e:
                        print(f"翻页失败: {e}")
                        break
                
            except TimeoutException:
                print(f"第 {page_num} 页加载超时")
                continue
            except Exception as e:
                print(f"处理第 {page_num} 页时出错: {e}")
                continue

        print(f"\n所有数据爬取完成！共处理了 {processed_count} 个美食")
        print("美食基本信息已实时保存到 '美食基本信息.csv'")
        print("各美食评论已分别保存到对应的CSV文件")

    except Exception as e:
        print(f"程序执行出错: {e}")

    finally:
        driver.quit()
        print("浏览器已关闭")

# 运行主程序
if __name__ == "__main__":
    main()

# %% [notebook cell 3]
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:44:00 2025
@author: Airble Dellen
携程美食爬虫：爬取美食名称、地点、人均、点评数、评分和详细评论信息
完整修复版本 - 修复美食名称提取问题并实现实时写入
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from bs4 import BeautifulSoup
import csv
import os
import re

def init_restaurant_csv():
    """初始化美食基本信息CSV文件"""
    filename = "美食基本信息.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["美食名称", "地点", "人均消费", "点评数", "列表页评分", "详情页评分"])
    return filename

def append_restaurant_data(restaurant_data, filename):
    """实时追加美食基本数据到CSV文件"""
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        detailed_score = restaurant_data.get('detailed_score', '未获取')
        writer.writerow([restaurant_data['name'], restaurant_data['location'], 
                       restaurant_data['price'], restaurant_data['review_count'], 
                       restaurant_data['score'], detailed_score])
    print(f"已保存: {restaurant_data['name']}")

            # 修改save_comment_data函数，将评论文件保存到fooddata目录
def save_comment_data(name, score, user, detail, data):
                """保存评论数据到fooddata目录下的CSV文件"""
                # 创建fooddata目录（如果不存在）
                if not os.path.exists('fooddata'):
                    os.makedirs('fooddata')
                
                # 清理文件名中的特殊字符
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
                filename = os.path.join('fooddata', f"{safe_name}_评论.csv")
                
                file_exists = os.path.isfile(filename)
                with open(filename, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["评分", "用户", "评论详情", "日期", "IP位置"])
                    
                    # 分离日期和IP位置
                    date = data[:10] if len(data) >= 10 else data
                    ip_location = data[10:] if len(data) > 10 else ""
                    writer.writerow([score, user, detail, date, ip_location])

def extract_restaurant_info_improved(driver):
    """改进版本：从当前页面提取美食信息"""
    restaurants = []
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    # 查找所有美食卡片
    restaurant_cards = soup.find_all("div", class_="list_mod2")
    print(f"找到 {len(restaurant_cards)} 个美食卡片")
    
    for idx, card in enumerate(restaurant_cards):
        try:
            print(f"\n--- 处理第 {idx + 1} 个美食卡片 ---")
            
            # 多种方法提取美食名称
            name = "未知美食"
            
            # 方法1：从 i.restaurant 元素提取（最直接的方法）
            restaurant_elem = card.find("i", class_="restaurant")
            if restaurant_elem:
                name_text = restaurant_elem.get_text(strip=True)
                if name_text and len(name_text) > 1:
                    name = name_text
                    print(f"方法1成功: {name}")
            
            # 方法2：从链接的title属性提取
            if name == "未知美食":
                link_elem = card.find("a", {"target": "_blank", "title": True})
                if link_elem:
                    title_text = link_elem.get('title', '').strip()
                    print(f"链接title: {title_text}")
                    if title_text:
                        # 处理title中的箭头分隔符
                        if '→' in title_text:
                            name = title_text.split('→')[-1].strip()
                        else:
                            name = title_text
                        print(f"方法2成功: {name}")
            
            # 方法3：从dt元素中提取（排除价格和评分）
            if name == "未知美食":
                dt_elem = card.find("dt")
                if dt_elem:
                    # 获取dt的直接文本内容，排除子元素
                    dt_text = ""
                    for content in dt_elem.contents:
                        if hasattr(content, 'string') and content.string:
                            dt_text += content.string.strip()
                        elif isinstance(content, str):
                            dt_text += content.strip()
                    
                    # 清理文本，去除价格、评分等信息
                    clean_text = re.sub(r'￥\d+|人均.*|条点评.*|\d+\.\d+分?|&nbsp;', '', dt_text).strip()
                    if clean_text and len(clean_text) > 2:
                        name = clean_text
                        print(f"方法3成功: {name}")
            
            # 方法4：从链接文本提取
            if name == "未知美食":
                link_elem = card.find("a", {"target": "_blank"})
                if link_elem:
                    link_text = link_elem.get_text(strip=True)
                    print(f"链接文本: {link_text}")
                    # 清理链接文本
                    clean_link_text = re.sub(r'￥\d+.*|人均.*|条点评.*|\d+\.\d+分?', '', link_text).strip()
                    if clean_link_text and len(clean_link_text) > 2:
                        name = clean_link_text
                        print(f"方法4成功: {name}")
            
            # 方法5：智能文本提取
            if name == "未知美食":
                print("使用智能文本提取...")
                
                # 查找所有包含中文的文本元素
                all_text_elements = card.find_all(text=True)
                chinese_texts = []
                for text in all_text_elements:
                    text_str = str(text).strip()
                    # 检查是否包含中文且不是价格/评分/无用信息
                    if (re.search(r'[\u4e00-\u9fff]', text_str) and 
                        len(text_str) > 2 and
                        not re.search(r'￥\d+|人均|条点评|\d+\.\d+分?|&nbsp;|^\s*$', text_str) and
                        text_str not in ['暂无', '评分', '点评']):
                        chinese_texts.append(text_str)
                
                print(f"找到的中文文本: {chinese_texts}")
                if chinese_texts:
                    # 选择最可能是餐厅名称的文本（通常是最长的或包含特定词汇的）
                    best_name = max(chinese_texts, key=lambda x: len(x) if any(word in x for word in ['餐厅', '酒店', '馆', '店', '坊', '轩', '楼']) else len(x) * 0.5)
                    name = best_name
                    print(f"方法5成功: {name}")
            
            # 提取地点信息
            location = "暂无地点信息"
            # 优先从 dd.ellipsis 提取
            location_elem = card.find("dd", class_="ellipsis")
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                if location_text and location_text != name:
                    location = location_text
            
            # 备用方案：从其他dd元素提取地址
            if location == "暂无地点信息":
                dd_elements = card.find_all("dd")
                for dd in dd_elements:
                    dd_text = dd.get_text(strip=True)
                    # 检查是否包含地址关键词
                    if any(keyword in dd_text for keyword in ["区", "路", "街", "巷", "号", "楼"]):
                        location = dd_text
                        break
            
            # 提取人均消费
            price = "暂无价格信息"
            price_elem = card.find("span", class_="price")
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # 提取价格数字
                price_match = re.search(r'￥\s*(\d+)', price_text)
                if price_match:
                    price = f"￥{price_match.group(1)}"
                elif price_text:
                    price = price_text
            
            # 提取点评数
            review_count = "暂无点评"
            review_elem = card.find("a", class_="recomment")
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                # 提取点评数字
                review_match = re.search(r'(\d+)条点评', review_text)
                if review_match:
                    review_count = f"{review_match.group(1)}条"
                elif review_text:
                    review_count = review_text
            
            # 提取评分
            score = "暂无评分"
            score_elem = card.find("span", class_="score")
            if score_elem:
                # 查找评分数字
                score_strong = score_elem.find("strong")
                if score_strong:
                    score = score_strong.get_text(strip=True)
                else:
                    score_text = score_elem.get_text(strip=True)
                    # 提取数字评分
                    score_match = re.search(r'(\d+\.?\d*)', score_text)
                    if score_match:
                        score = score_match.group(1)
                    elif score_text:
                        score = score_text
            
            restaurant_data = {
                'name': name,
                'location': location,
                'price': price,
                'review_count': review_count,
                'score': score
            }
            
            restaurants.append(restaurant_data)
            
            print(f"✓ 提取成功 - 美食: {name}")
            print(f"  地点: {location}")
            print(f"  人均: {price}")
            print(f"  点评: {review_count}")
            print(f"  评分: {score}")
            
        except Exception as e:
            print(f"提取第 {idx + 1} 个美食信息时出错: {e}")
            continue
    
    return restaurants

def extract_detailed_score(driver):
    """提取美食详情页的详细评分"""
    try:
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        # 根据你提供的HTML结构，查找detailtop_r_info中的评分
        detail_info = soup.find("ul", class_="detailtop_r_info")
        if detail_info:
            # 查找第一个li元素
            score_li = detail_info.find("li")
            if score_li:
                # 查找span.score元素
                score_span = score_li.find("span", class_="score")
                if score_span:
                    # 查找b标签中的评分数字
                    score_b = score_span.find("b")
                    if score_b:
                        score_text = score_b.get_text(strip=True)
                        return score_text
        
        # 备用方案：直接查找span.score
        score_elem = soup.find("span", class_="score")
        if score_elem:
            # 查找b标签
            score_b = score_elem.find("b")
            if score_b:
                return score_b.get_text(strip=True)
            else:
                # 如果没有b标签，直接返回span的文本
                detailed_score = score_elem.get_text(strip=True)
                return detailed_score
        
        # 尝试查找包含数字评分的b标签
        score_elem = soup.find("b", string=re.compile(r'\d+\.\d+'))
        if score_elem:
            return score_elem.get_text(strip=True)
            
        return "暂无详细评分"
        
    except Exception as e:
        print(f"提取详细评分时出错: {e}")
        return "暂无详细评分"

def scrape_restaurant_comments(driver, restaurant_name, max_pages=5):
    """爬取单个美食的评论信息"""
    print(f"\n开始爬取 {restaurant_name} 的评论...")
    
    previous_first_user = None
    comment_count = 0
    
    # 爬取评论
    for page_num in range(1, max_pages + 1):
        try:
            time.sleep(3)
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')
            
            # 根据新的HTML结构查找评论
            # 查找评论容器
            comment_box = soup.find("div", {"id": "sightcommentbox"})
            if comment_box:
                # 查找所有评论项
                chats = comment_box.find_all("div", {"class": "comment_single"})
            else:
                # 备用选择器
                chats = soup.find_all("div", {"class": "comment_single"})
            
            if not chats:
                print("没有更多评论，结束爬取。")
                break
            
            # 检查是否到达最后一页
            if len(chats) > 0:
                first_comment = chats[0]
                current_first_user = None
                
                # 获取用户名 - 根据新结构调整
                usering_elem = first_comment.find("div", {"class": "usering"})
                if usering_elem:
                    user_link = usering_elem.find("a")
                    if user_link:
                        current_first_user = user_link.get_text(strip=True)
                
                if previous_first_user is not None and current_first_user == previous_first_user:
                    print("到达最后一页，结束爬取。")
                    break
                
                previous_first_user = current_first_user
            
            # 提取评论信息
            for chat in chats:
                try:
                    # 提取用户名
                    user = "匿名用户"
                    usering_elem = chat.find("div", {"class": "usering"})
                    if usering_elem:
                        user_link = usering_elem.find("a")
                        if user_link:
                            user = user_link.get_text(strip=True)
                        else:
                            # 尝试从span.ellipsis获取
                            ellipsis_span = usering_elem.find("span", {"class": "ellipsis"})
                            if ellipsis_span:
                                user_link = ellipsis_span.find("a")
                                if user_link:
                                    user = user_link.get_text(strip=True)
                    
                    # 提取评论内容
                    detail = "无评论内容"
                    main_con = chat.find("li", {"class": "main_con"})
                    if main_con:
                        heightbox = main_con.find("span", {"class": "heightbox"})
                        if heightbox:
                            # 获取评论文本，移除HTML标签
                            detail_text = heightbox.get_text(strip=True)
                            if detail_text:
                                detail = detail_text
                    
                    # 提取评分 - 从title_cf或其他位置
                    score = "无评分"
                    title_cf = chat.find("li", {"class": "title_cf"})
                    if title_cf:
                        # 尝试从星级或评分元素中获取评分
                        score_text = title_cf.get_text(strip=True)
                        if score_text:
                            score = score_text
                    
                    # 提取时间和位置信息
                    data = "无时间信息"
                    # 尝试从commenttoggle或其他位置获取时间
                    toggle_elem = chat.find("p", {"class": "commenttoggle"})
                    if toggle_elem:
                        data = toggle_elem.get_text(strip=True)
                    
                    # 只保存有内容的评论
                    if detail != "无评论内容" and len(detail.strip()) > 5:  # 至少5个字符
                        save_comment_data(restaurant_name, score, user, detail, data)
                        comment_count += 1
                        print(f"评分: {score}, 用户: {user[:10]}...")  # 只显示用户名前10个字符
                    
                except Exception as e:
                    print(f"提取单条评论时出错: {e}")
                    continue
            
            # 翻到下一页
            if page_num < max_pages:
                try:
                    # 查找下一页按钮
                    next_button = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')] | //a[contains(@class, 'next')] | //a[@class='cf' and contains(@href, 'p')]")
                    if next_button.is_enabled():
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                    else:
                        print("已到最后一页")
                        break
                except Exception as e:
                    print(f"翻页失败: {e}")
                    break
                        
        except Exception as e:
            print(f"处理第 {page_num} 页评论时出错: {e}")
            continue
    
    print(f"{restaurant_name} 评论爬取完成，共获取 {comment_count} 条评论")

def debug_single_card(driver, card_index=0):
    """调试单个美食卡片的详细结构"""
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    
    restaurant_cards = soup.find_all("div", class_="list_mod2")
    
    if card_index < len(restaurant_cards):
        card = restaurant_cards[card_index]
        print(f"\n=== 第 {card_index + 1} 个美食卡片详细结构 ===")
        print(card.prettify())
        
        print(f"\n=== 文本内容分析 ===")
        # 分析所有文本内容
        all_texts = card.find_all(text=True)
        for i, text in enumerate(all_texts):
            text_str = str(text).strip()
            if text_str:
                print(f"文本{i}: '{text_str}' (父元素: {text.parent.name if text.parent else 'None'})")
        
        print(f"\n=== 关键元素分析 ===")
        # 分析关键元素
        i_restaurant = card.find("i", class_="restaurant")
        if i_restaurant:
            print(f"i.restaurant: '{i_restaurant.get_text(strip=True)}'")
        
        dt_elem = card.find("dt")
        if dt_elem:
            print(f"dt元素: '{dt_elem.get_text(strip=True)}'")
            print(f"dt的HTML: {dt_elem}")
        
        links = card.find_all("a")
        for i, link in enumerate(links):
            print(f"链接{i}: href='{link.get('href', '')}', title='{link.get('title', '')}', text='{link.get_text(strip=True)}'")
    else:
        print(f"卡片索引 {card_index} 超出范围，共找到 {len(restaurant_cards)} 个卡片")

def main():
    # 配置Chrome驱动路径 - 请修改为你的chromedriver路径
    service = Service(r"F:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    
    # 配置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        # 初始化CSV文件
        csv_filename = init_restaurant_csv()
        
        # 访问美食列表页面
        url = "https://you.ctrip.com/restaurantlist/Guizhou100064/list-c4914-p1.html?ordertype=0"
        driver.get(url)
        print("页面标题:", driver.title)
        time.sleep(5)

        # 可选：调试第一个卡片的结构
        print("\n=== 是否需要调试页面结构？(y/n) ===")
        debug_choice = input("输入y查看调试信息，输入n直接开始爬取: ")
        if debug_choice.lower() == 'y':
            debug_single_card(driver, 0)
            print("\n调试完成，开始正式爬取...")
            time.sleep(2)
        
        processed_count = 0

        # 爬取前5页美食信息和评论（实时处理）
        for page_num in range(1, 6):  # 爬取5页
            print(f"\n{'='*50}")
            print(f"正在处理第 {page_num} 页...")
            print(f"{'='*50}")
            
            try:
                # 等待页面加载
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list_mod2")))
                
                # 提取美食信息
                restaurants = extract_restaurant_info_improved(driver)
                if not restaurants:
                    print(f"第 {page_num} 页未获取到美食数据")
                    continue
                
                print(f"第 {page_num} 页获取到 {len(restaurants)} 个美食")
                
                # 获取当前页面的美食卡片元素（用于点击）
                restaurant_cards = driver.find_elements(By.CLASS_NAME, "list_mod2")
                
                # 逐个处理每个美食
                for i, restaurant_info in enumerate(restaurants):
                    try:
                        print(f"\n{'='*30}")
                        print(f"正在处理: {restaurant_info['name']} ({i+1}/{len(restaurants)})")
                        print(f"{'='*30}")
                        
                        # 重新获取当前页面的美食卡片（防止页面元素失效）
                        current_cards = driver.find_elements(By.CLASS_NAME, "list_mod2")
                        if i >= len(current_cards):
                            print(f"无法找到第{i+1}个美食卡片，跳过")
                            append_restaurant_data(restaurant_info, csv_filename)
                            continue
                        
                        restaurant_card = current_cards[i]
                        
                        # 获取美食详情页链接
                        try:
                            detail_link = restaurant_card.find_element(By.CSS_SELECTOR, "a[target='_blank']")
                            detail_url = detail_link.get_attribute('href')
                            
                            if detail_url:
                                print(f"访问详情页: {detail_url}")
                                # 在新标签页中打开详情页
                                driver.execute_script("window.open(arguments[0]);", detail_url)
                                time.sleep(3)
                                
                                # 切换到新标签页
                                driver.switch_to.window(driver.window_handles[-1])
                                time.sleep(3)
                                
                                # 获取详细评分
                                detailed_score = extract_detailed_score(driver)
                                restaurant_info['detailed_score'] = detailed_score
                                print(f"详细评分：{detailed_score}")
                                
                                # 爬取该美食的评论
                                scrape_restaurant_comments(driver, restaurant_info['name'], max_pages=3)  # 减少页数提高效率
                                
                                # 关闭当前标签页，回到主页面
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                                time.sleep(1)
                            else:
                                print("未找到详情页链接")
                                
                        except Exception as link_error:
                            print(f"处理详情页链接时出错: {link_error}")
                        
                        # 实时保存美食基本信息
                        append_restaurant_data(restaurant_info, csv_filename)
                        processed_count += 1
                        print(f"已处理 {processed_count} 个美食")
                        
                    except Exception as e:
                        print(f"处理美食 {restaurant_info.get('name', '未知')} 时出错: {e}")
                        # 确保回到主标签页
                        try:
                            if len(driver.window_handles) > 1:
                                driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                        # 仍然保存基本信息
                        try:
                            append_restaurant_data(restaurant_info, csv_filename)
                        except:
                            pass
                        continue
                
                # 翻到下一页
                if page_num < 5:
                    try:
                        print(f"\n准备翻到第 {page_num + 1} 页...")
                        next_button = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')] | //a[contains(@class, 'next')]")
                        if next_button.is_enabled():
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(5)
                            print(f"成功翻到第 {page_num + 1} 页")
                        else:
                            print("已到最后一页，停止爬取")
                            break
                    except NoSuchElementException:
                        print("未找到下一页按钮，停止爬取")
                        break
                    except Exception as e:
                        print(f"翻页失败: {e}")
                        break
                
            except TimeoutException:
                print(f"第 {page_num} 页加载超时")
                continue
            except Exception as e:
                print(f"处理第 {page_num} 页时出错: {e}")
                continue

        print(f"\n{'='*60}")
        print(f"所有数据爬取完成！共处理了 {processed_count} 个美食")
        print("美食基本信息已实时保存到 '美食基本信息.csv'")
        print("各美食评论已分别保存到对应的CSV文件")
        print(f"{'='*60}")

    except Exception as e:
        print(f"程序执行出错: {e}")

    finally:
        try:
            driver.quit()
            print("浏览器已关闭")
        except:
            pass

# 运行主程序
if __name__ == "__main__":
    main()
