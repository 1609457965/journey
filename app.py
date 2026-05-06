import os
from flask import Flask, render_template, jsonify, request, send_from_directory
import pandas as pd
import jieba
from wordcloud import WordCloud
import base64
from io import BytesIO
import json
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 字体路径设置
FONT_PATH = 'static/SimHei.ttf'
if not os.path.exists(FONT_PATH):
    print(f"警告: 字体文件 {FONT_PATH} 未找到。")
    FONT_PATH = None

# 全局数据缓存
cached_data = {
    'attractions': None,
    'food': None,
    'hotels': None,
    'transport': None
}


def load_attractions_data():
    """加载景点数据"""
    if cached_data['attractions'] is None:
        try:
            df = pd.read_csv('贵州景点基本信息.csv', encoding='utf-8')
            # 清理数据 - 修复评分转换逻辑
            df['评分_数值'] = df['评分'].str.replace('分', '').replace(['暂无评分', '暂无评'], '0').astype(float)
            # 选择评分最高的20个景点
            df_top = df

            attractions = []
            for _, row in df_top.iterrows():
                # 使用远程图片链接，不再需要本地placeholder
                image_url = row['图片链接']
                attraction = {
                    'id': f"a{_}",
                    'name': row['景点名称'].split(',')[0].strip(),  # 例如："黄果树景区"
                    'fullName': row['景点名称'],  # 完整名称，包含地点
                    'location': row['景点名称'].split(',')[1].strip() if ',' in row['景点名称'] else '',  # 例如："镇宁"
                    'rating': row['评分'],  # 保持原格式，例如："4.5分"
                    'ratingNum': row['评分人数'],  # "暂无评分人数"
                    'image': image_url  # 使用携程网的图片链接
                }
                attractions.append(attraction)

            cached_data['attractions'] = attractions
        except Exception as e:
            print(f"加载景点数据失败: {e}")
            cached_data['attractions'] = []

    return cached_data['attractions']


def generate_wordcloud(comments, output_path):
    """生成词云图并保存"""
    try:
        text = ' '.join(comments)
        wc = WordCloud(font_path='simhei.ttf', width=800, height=400, background_color='white')
        wc.generate(text)
        wc.to_file(output_path)
    except Exception as e:
        print(f"[错误] 生成词云失败: {e}")

def load_food_data():
    """加载美食信息和评论词云"""
    if cached_data['food'] is None:
        try:
            food_df = pd.read_csv('美食基本信息.csv')

            food_data = []
            for _, row in food_df.iterrows():
                name = row['美食名称']
                location = row['地点']
                avg_price = row['人均消费']
                rating = row['详情页评分'] if row['详情页评分'] != '暂无评分' else '无评分'

                # 评论文件路径
                comment_file = os.path.join('fooddata', f"{name}_评论.csv")
                wordcloud_file = os.path.join('wordcloud_images', f"{name}_wordcloud.png")

                # 使用词云图作为默认图片
                image_path = wordcloud_file if os.path.exists(wordcloud_file) else None

                food_item = {
                    'id': f"f_{_}",
                    'name': name,
                    'type': '未知分类',
                    'rating': f"{rating}分" if rating != '无评分' else '暂无评分',
                    'avgPrice': avg_price,
                    'location': location,
                    'wordcloudImage': image_path,
                    'image': image_path  # 使用词云图替代食物图片
                }
                food_data.append(food_item)

            cached_data['food'] = food_data
        except Exception as e:
            print(f"[错误] 加载美食数据失败: {e}")
            cached_data['food'] = []

    return cached_data['food']

import csv

def load_hotels_data():
    """从CSV加载酒店数据并缓存"""
    if cached_data['hotels'] is None:
        try:
            hotels_data = []
            with open('hotel_贵州.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    hotels_data.append({
                        'id': f'h{idx+1}',
                        'name': row['酒店名称'],
                        'price': f"¥{row['酒店价格']}/晚",
                        'address': row['酒店地址'],
                        'location': row['酒店位置'],
                        'intro': row['酒店简介'],
                        'rating_text': row['酒店评价'],
                        'rating_score': float(row['酒店评分']),
                        'reviews': int(row['酒店评论数'].replace(',', '').strip()),
                        'tags': row['酒店标签'],
                        'image': row['酒店图片']
                    })
            cached_data['hotels'] = hotels_data
        except Exception as e:
            print(f"加载酒店数据失败: {e}")
            cached_data['hotels'] = []

    return cached_data['hotels']



def load_transport_data():
    """加载交通数据"""
    if cached_data['transport'] is None:
        try:
            transport_data = []
            
            # 加载飞机数据
            try:
                fly_df = pd.read_csv('flydata/上海-贵阳.csv', encoding='utf-8')
                for idx, row in fly_df.iterrows():
                    # 处理日期和时间
                    departure_time = f"{row['出发时间']}"
                    arrival_time = f"{row['到达时间']}"
                    
                    transport_data.append({
                        'id': f'f{idx+1}',
                        'name': f"{row['航班号']} {row['出发城市']}-{row['到达城市']}",
                        'type': '飞机',
                        'duration': f"{row['飞行时长']}分钟",
                        'price': f"¥{row['economy_total']}",  # 使用经济舱总价
                        'time': f"{departure_time}-{arrival_time}",
                        'departure': f"{row['出发机场']}T{row['departureTerminal']}",
                        'arrival': f"{row['到达机场']}T{row['arrivalTerminal']}",
                        'airline': row['航空公司'],
                        'image': '/static/plane.jpg'
                    })
            except Exception as e:
                print(f"加载飞机数据失败: {e}")

            # 加载火车数据
            try:
                train_df = pd.read_csv('train_data/上海到贵州各城市_2025-06-05.csv', encoding='utf-8')
                for idx, row in train_df.iterrows():
                    # 获取合适的票价（优先使用二等座，如果没有则使用硬座）
                    price = row['二等座价格']
                    if pd.isna(price) or price == '无':
                        price = row['硬座价格']
                        if pd.isna(price) or price == '无':
                            continue  # 跳过没有票价的车次
                            
                    transport_data.append({
                        'id': f't{idx+1}',
                        'name': f"{row['车次']} {row['出发站']}-{row['到达站']}",
                        'type': '高铁' if row['车次'].startswith('G') else '火车',
                        'duration': row['历时'],
                        'price': price,  # 已包含¥符号
                        'time': f"{row['出发时间']}-{row['到达时间']}",
                        'departure': row['出发站'],
                        'arrival': row['到达站'],
                        'image': '/static/train.jpg'
                    })
            except Exception as e:
                print(f"加载火车数据失败: {e}")

            if not transport_data:
                raise Exception("未能加载任何交通数据")

            cached_data['transport'] = transport_data

        except Exception as e:
            print(f"加载交通数据失败: {e}")
            cached_data['transport'] = []

    return cached_data['transport']


# 路由定义
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommendation')
def recommendation_page():
    return render_template('recommendation.html')


@app.route('/api/attractions')
def get_attractions():
    """获取景点数据API"""
    attractions = load_attractions_data()
    return jsonify(attractions)


@app.route('/api/food')
def get_food():
    """获取美食数据API"""
    food = load_food_data()
    return jsonify(food)


@app.route('/api/hotels')
def get_hotels():
    """获取酒店数据API"""
    hotels = load_hotels_data()
    return jsonify(hotels)


@app.route('/api/transport')
def get_transport():
    """获取交通数据API"""
    transport = load_transport_data()
    return jsonify(transport)


@app.route('/api/generate_recommendations', methods=['POST'])
def generate_recommendations():
    """生成推荐方案API"""
    try:
        data = request.json
        selected_items = data.get('selectedItems', {})

        # 验证是否每个类别都有选择
        for category in ['attractions', 'food', 'hotels', 'transport']:
            if not selected_items.get(category):
                return jsonify({'error': f'请至少选择一个{category}'}), 400

        # 生成推荐方案
        recommendations = []

        # 推荐方案模板
        templates = [
            {
                'title': '经典贵州深度游',
                'theme': 'classic',
                'reason': '这个方案涵盖了贵州最具代表性的景点和美食，适合第一次来贵州的游客。合理的行程安排让您既能欣赏壮丽的自然风光，又能品尝地道的贵州美食，配合舒适的住宿，让您的旅程轻松愉快。'
            },
            {
                'title': '自然风光探索之旅',
                'theme': 'nature',
                'reason': '专注于贵州独特的自然景观，从瀑布到喀斯特地貌，让您充分领略大自然的鬼斧神工。搭配当地特色美食和便捷的交通安排，是摄影爱好者和自然风光爱好者的最佳选择。'
            },
            {
                'title': '民族文化体验之旅',
                'theme': 'culture',
                'reason': '深入体验贵州多彩的民族文化，从苗寨到侗寨，感受不同民族的风情。品尝各具特色的民族美食，入住特色民宿，让您的旅程充满文化韵味。'
            },
            {
                'title': '休闲度假之旅',
                'theme': 'leisure',
                'reason': '注重舒适和放松，选择交通便利的景点和高品质的住宿，让您在欣赏美景的同时充分休息。适合家庭出游或追求品质的旅行者。'
            },
            {
                'title': '美食寻味之旅',
                'theme': 'food',
                'reason': '以贵州特色美食为主题，带您品尝最地道的酸汤鱼、丝娃娃等美食。结合景点游览，让您的味蕾和视觉都得到极大满足。'
            }
        ]

        # 生成3-5个推荐方案
        num_recommendations = min(len(templates), random.randint(3, 5))
        selected_templates = random.sample(templates, num_recommendations)

        for i, template in enumerate(selected_templates):
            recommendation = {
                'id': i + 1,
                'title': template['title'],
                'theme': template['theme'],
                'items': {},
                'reason': template['reason']
            }

            # 为每个类别随机选择项目
            for category in ['attractions', 'food', 'hotels', 'transport']:
                items = selected_items[category]
                if len(items) > 2:
                    # 如果选择了多个，随机选1-2个
                    num_items = random.randint(1, min(2, len(items)))
                    selected = random.sample(items, num_items)
                else:
                    selected = items

                recommendation['items'][category] = selected

            recommendations.append(recommendation)

        return jsonify({'recommendations': recommendations})

    except Exception as e:
        print(f"生成推荐失败: {e}")
        return jsonify({'error': str(e)}), 500


# 继承原有的路由
@app.route('/search_attractions')
def search_attractions():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "请输入地点"}), 400

    filename = f"{location}景点基本信息.csv"
    if not os.path.exists(filename):
        return jsonify({"error": f"未找到 {filename}"}), 404

    try:
        df = pd.read_csv(filename, encoding='utf-8')
        df['景点简称'] = df['景点名称'].apply(lambda x: x.split(',')[0].strip())
        df['有评论'] = df['景点简称'].apply(lambda x:
                                            os.path.exists(os.path.join("景点评论", f"{x}_评论.csv")))

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": f"读取或处理CSV失败: {str(e)}"}), 500


@app.route('/get_comments')
def get_comments():
    attraction_name = request.args.get('name')
    if not attraction_name:
        return jsonify({"error": "请输入景点名称"}), 400

    simple_attraction_name = attraction_name.split(',')[0].strip()
    comment_filename = os.path.join("景点评论", f"{simple_attraction_name}_评论.csv")

    if not os.path.exists(comment_filename):
        return jsonify({"error": f"未找到评论文件: {comment_filename}"}), 404

    try:
        df_comments = pd.read_csv(comment_filename, encoding='utf-8')
        df_comments = df_comments.replace({pd.NA: None})
        comments_data = df_comments.where(pd.notnull(df_comments), None).to_dict(orient='records')

        text = " ".join(df_comments['评论详情'].fillna('').astype(str).tolist())
        if not text.strip():
            return jsonify({"comments": comments_data, "wordcloud_image": None, "error": "评论内容为空，无法生成词云"})

        word_list = jieba.lcut(text)
        filtered_words = [word for word in word_list if len(word) > 1]
        text_for_wordcloud = " ".join(filtered_words)

        if not text_for_wordcloud.strip():
            return jsonify(
                {"comments": comments_data, "wordcloud_image": None, "error": "有效评论词汇为空，无法生成词云"})

        wc_params = {'background_color': "white", 'max_words': 100, 'width': 400, 'height': 300}
        if FONT_PATH:
            wc_params['font_path'] = FONT_PATH

        wordcloud = WordCloud(**wc_params).generate(text_for_wordcloud)

        img_buffer = BytesIO()
        wordcloud.to_image().save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        return jsonify({"comments": comments_data, "wordcloud_image": "data:image/png;base64," + img_base64})
    except Exception as e:
        return jsonify({"error": f"生成词云或读取评论失败: {str(e)}"}), 500


@app.route('/recommend')
def recommend():
    return render_template('recommend.html')


@app.route('/get_recommendations')
def get_recommendations():
    try:
        df = pd.read_csv('贵州景点基本信息.csv', encoding='utf-8')
        df['评分'] = df['评分'].replace('暂无评分', '0分')
        df['评分_数值'] = df['评分'].str.replace('分', '').astype(float)
        df_sorted = df.sort_values('评分_数值', ascending=False)
        df_sorted = df_sorted.drop('评分_数值', axis=1)

        return jsonify(df_sorted.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 静态文件服务
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/wordcloud_images/<path:path>')
def send_wordcloud(path):
    return send_from_directory('wordcloud_images', path)


if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('wordcloud_images', exist_ok=True)

    app.run(debug=True, port=5001)