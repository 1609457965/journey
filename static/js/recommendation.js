// recommendation.js - 推荐页面脚本

// 获取URL参数
function getUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        selectedItems: urlParams.get('selectedItems') ? JSON.parse(decodeURIComponent(urlParams.get('selectedItems'))) : null,
        recommendations: urlParams.get('recommendations') ? JSON.parse(decodeURIComponent(urlParams.get('recommendations'))) : null
    };
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    const params = getUrlParams();
    if (params.recommendations) {
        displayRecommendations(params.recommendations);
    } else {
        loadRecommendationData();
    }
});

// 加载推荐数据
async function loadRecommendationData() {
    try {
        const response = await fetch('/get_recommendations');
        if (response.ok) {
            const data = await response.json();
            displayAttractionsList(data);
        } else {
            throw new Error('获取推荐数据失败');
        }
    } catch (error) {
        console.error('加载推荐数据失败:', error);
        document.getElementById('content').innerHTML = `
            <div style="text-align: center; padding: 50px; color: #e74c3c;">
                <h3>加载数据失败</h3>
                <p>请刷新页面重试</p>
                <button onclick="location.reload()" style="padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    刷新页面
                </button>
            </div>
        `;
    }
}

// 显示景点列表（原始推荐页面）
function displayAttractionsList(attractions) {
    const content = document.getElementById('content');

    if (!attractions || attractions.length === 0) {
        content.innerHTML = `
            <div style="text-align: center; padding: 50px; color: #7f8c8d;">
                <h3>暂无推荐数据</h3>
                <p>请稍后再试</p>
            </div>
        `;
        return;
    }

    let html = `
        <div style="background: white; border-radius: 15px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 20px; text-align: center;">🌟 贵州热门景点推荐</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
    `;

    attractions.slice(0, 12).forEach((attraction, index) => {
        html += `
            <div style="border: 1px solid #ecf0f1; border-radius: 10px; padding: 15px; background: #f8f9fa; transition: all 0.3s; cursor: pointer;"
                 onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 5px 15px rgba(0,0,0,0.1)'"
                 onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
                 onclick="selectAttraction('${attraction.景点名称}', '${attraction.评分}')">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                        ${index + 1}
                    </span>
                    <h4 style="color: #2c3e50; margin: 0; flex: 1;">${attraction.景点名称.split(',')[0]}</h4>
                </div>
                <p style="color: #7f8c8d; margin: 5px 0;">${attraction.景点名称.includes(',') ? attraction.景点名称.split(',')[1] : ''}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #e74c3c; font-weight: bold;">⭐ ${attraction.评分}</span>
                    <span style="color: #27ae60; font-size: 0.9em;">${attraction.评分人数 || '推荐景点'}</span>
                </div>
            </div>
        `;
    });

    html += `
            </div>
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; transition: all 0.3s;"
                   onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 5px 15px rgba(52, 152, 219, 0.3)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    🎯 进入综合推荐系统
                </a>
            </div>
        </div>
    `;

    content.innerHTML = html;
}

// 选择景点（如果需要与原系统兼容）
function selectAttraction(name, rating) {
    console.log('选择景点:', name, rating);
    // 可以添加选择景点的逻辑
}

// 显示推荐方案（来自主页面的推荐结果）
function displayRecommendations(recommendations) {
    const content = document.getElementById('content');

    let html = `
        <div style="background: white; border-radius: 15px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 30px;">
                ✨ 您的个性化推荐方案
            </h2>
    `;

    recommendations.forEach((rec, index) => {
        html += createRecommendationCardHTML(rec, index + 1);
    });

    html += `
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; transition: all 0.3s; margin-right: 15px;"
                   onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 5px 15px rgba(52, 152, 219, 0.3)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    🔄 重新选择
                </a>
                <button onclick="printRecommendations()" style="background: linear-gradient(135deg, #27ae60, #229954); color: white; padding: 12px 30px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; transition: all 0.3s;"
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 5px 15px rgba(39, 174, 96, 0.3)'"
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    📄 保存方案
                </button>
            </div>
        </div>
    `;

    content.innerHTML = html;
}

// 创建推荐卡片HTML
function createRecommendationCardHTML(recommendation, number) {
    const categoriesHTML = renderRecommendationCategoriesHTML(recommendation.items);

    return `
        <div style="border: 2px solid #ecf0f1; border-radius: 12px; padding: 25px; margin-bottom: 20px; background: linear-gradient(135deg, #f8f9fa, #fff); transition: all 0.3s;"
             onmouseover="this.style.borderColor='#3498db'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.1)'"
             onmouseout="this.style.borderColor='#ecf0f1'; this.style.boxShadow='none'">
            
            <div style="display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #ecf0f1;">
                <div style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2em; margin-right: 15px;">
                    ${number}
                </div>
                <h3 style="flex: 1; color: #2c3e50; font-size: 1.3em; margin: 0;">${recommendation.title}</h3>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px;">
                ${categoriesHTML}
            </div>
            
            <div style="background: #e8f4f8; padding: 15px; border-radius: 8px;">
                <h5 style="color: #2980b9; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                    💡 推荐理由
                </h5>
                <p style="color: #555; line-height: 1.6; margin: 0;">${recommendation.reason}</p>
            </div>
        </div>
    `;
}

// 渲染推荐分类内容HTML
function renderRecommendationCategoriesHTML(items) {
    let html = '';

    if (items.attractions && items.attractions.length > 0) {
        html += createRecommendationCategoryHTML('🏞️ 景点', items.attractions, 'attractions');
    }

    if (items.food && items.food.length > 0) {
        html += createRecommendationCategoryHTML('🍜 美食', items.food, 'food');
    }

    if (items.hotels && items.hotels.length > 0) {
        html += createRecommendationCategoryHTML('🏨 酒店', items.hotels, 'hotels');
    }

    if (items.transport && items.transport.length > 0) {
        html += createRecommendationCategoryHTML('🚄 交通', items.transport, 'transport');
    }

    return html;
}

// 创建推荐分类HTML
function createRecommendationCategoryHTML(title, items, category) {
    const itemsList = items.map(item => `
        <li style="padding: 5px 0; color: #555; font-size: 0.9em; border-bottom: 1px solid #f0f0f0; margin-bottom: 5px;">
            ${getRecommendationItemDisplayHTML(item, category)}
        </li>
    `).join('');

    return `
        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
            <h5 style="color: #34495e; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                ${title}
            </h5>
            <ul style="list-style: none; padding: 0; margin: 0;">
                ${itemsList}
            </ul>
        </div>
    `;
}

// 获取推荐项目显示文本HTML
function getRecommendationItemDisplayHTML(item, category) {
    switch(category) {
        case 'attractions':
            return `<strong>${item.name}</strong><br><small style="color: #7f8c8d;">评分: ${item.rating}</small>`;
        case 'food':
            return `<strong>${item.name}</strong><br><small style="color: #7f8c8d;">${item.type} - ${item.avgPrice}</small>`;
        case 'hotels':
            return `<strong>${item.name}</strong><br><small style="color: #7f8c8d;">${item.location} - ${item.price}</small>`;
        case 'transport':
            return `<strong>${item.name}</strong><br><small style="color: #7f8c8d;">${item.duration} - ${item.price}</small>`;
        default:
            return item.name;
    }
}

// 保存/打印推荐方案
function printRecommendations() {
    window.print();
}