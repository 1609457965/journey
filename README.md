# 贵州旅游综合推荐系统

这是一个基于 Flask 的贵州旅游推荐小项目，整合景点、美食、酒店、交通数据，并提供网页展示、评论查看、词云生成和组合推荐接口。

## 项目结构

```text
.
├── app.py                  # Flask 主应用和 API
├── run.py                  # 环境检查与启动脚本
├── setup.py                # 示例数据/项目初始化辅助脚本
├── templates/              # 页面模板
├── static/                 # CSS、JS 和页面图片资源
├── flydata/                # 航班数据
├── train_data/             # 火车/高铁数据
├── fooddata/               # 美食评论数据
├── 景点评论/               # 景点评论数据
├── wordcloud_images/       # 已生成的美食词云图片
├── 贵州景点基本信息.csv
├── 美食基本信息.csv
└── hotel_贵州.csv
```

## 运行方式

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

也可以直接运行：

```bash
python app.py
```

应用默认地址：

- `http://127.0.0.1:5000/`（通过 `run.py` 启动）
- `http://127.0.0.1:5001/`（直接运行 `app.py`）

## 说明

- `static/SimHei.ttf` 未纳入 Git，主要是避免提交较大的字体文件和潜在授权问题；如需更好的中文词云显示，可在本地将可用中文字体放到该路径。
- `.idea/`、`__pycache__/`、日志和临时文件已通过 `.gitignore` 排除。
