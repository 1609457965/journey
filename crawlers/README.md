# 爬虫代码说明

本目录整理了课程项目中使用过的采集代码，来源包括：

- `G:\homework\DataCollection\Python-爬虫爬取豆果网和美食网的菜单\SpiderRecipes-master`
- `G:\homework\DataCollection\脚本`

## 目录结构

```text
crawlers/
├── recipes/                         # 豆果网、美食天下菜谱爬虫原始 Python 脚本
├── scripts/                         # 从 notebook 提取出的采集源码
└── requirements-crawlers.txt         # 爬虫相关依赖
```

## scripts 文件说明

- `qunar_train_tickets.py`：去哪儿火车票 Selenium 采集逻辑，来源于 `all_train_ticket.ipynb`。
- `ctrip_food_spider.py`：携程贵州美食、餐厅详情和评论采集逻辑，来源于 `foodmark.ipynb`。
- `ctrip_guizhou_attraction_spider.py`：携程贵州景点基本信息、评分、评论采集逻辑，来源于 `scen.ipynb`。
- `ctrip_shanxi_attraction_spider.py`：携程山西古建景点采集示例，来源于 `mark.ipynb`。
- `douban_books_spider.py`：豆瓣图书 Top250 requests/BeautifulSoup 采集示例，来源于 `mp4_totext.ipynb` 中的爬虫单元。
- `crawler_experiments.py`：综合探索代码，包含去哪儿门票、去哪儿火车、携程酒店 API、航班和景点采集等片段，来源于 `crap.ipynb`。Notebook 输出已去除。

## 注意事项

- notebook 中的执行输出没有提交，只保留源码，避免把大体积调试结果上传到 GitHub。
- 携程酒店接口实验代码中复制过的 `phantom-token` 和 Cookie 已替换为本地占位符，需要运行时自行抓取或补充。
- Selenium 相关脚本需要本机安装 Chrome/Edge 浏览器及匹配的 WebDriver。
- 爬虫脚本依赖目标网站页面结构，若网站改版，选择器和接口参数可能需要同步调整。
