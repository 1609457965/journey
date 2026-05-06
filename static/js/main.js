
// main.js 全局变量
let selectedItems = {
    attractions: [],
    food: [],
    hotels: [],
    transport: []
};

let allData = {
    attractions: [],
    food: [],
    hotels: [],
    transport: []
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadAllData();
});

// 加载所有数据
async function loadAllData() {
    try {
        const [attractions, food, hotels, transport] = await Promise.all([
            fetch('/api/attractions').then(res => res.json()),
            fetch('/api/food').then(res => res.json()),
            fetch('/api/hotels').then(res => res.json()),
            fetch('/api/transport').then(res => res.json())
        ]);

        allData.attractions = attractions;
        allData.food = food;
        allData.hotels = hotels;
        allData.transport = transport;

        // 渲染默认显示的景点数据
        renderAttractions();
    } catch (error) {
        console.error('加载数据失败:', error);
        alert('数据加载失败，请刷新页面重试');
    }
}

// 标签切换功能
function showTab(tabName) {
    // 移除所有标签的active类
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // 激活当前标签
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // 根据标签渲染对应数据
    switch(tabName) {
        case 'attractions':
            renderAttractions();
            break;
        case 'food':
            renderFood();
            break;
        case 'hotels':
            renderHotels();
            break;
        case 'transport':
            renderTransport();
            break;
    }
}

// 渲染景点数据
function renderAttractions() {
    const grid = document.getElementById('attractions-grid');
    grid.innerHTML = '';

    allData.attractions.forEach(attraction => {
        const isSelected = selectedItems.attractions.some(item => item.id === attraction.id);
        const card = createItemCard(attraction, 'attractions', {
            title: attraction.name,
            subtitle: attraction.location,
            rating: attraction.rating,
            extra: `评价人数: ${attraction.ratingNum}`,
            image: attraction.image
        }, isSelected);
        grid.appendChild(card);
    });
}

// 渲染美食数据
function renderFood() {
    const grid = document.getElementById('food-grid');
    grid.innerHTML = '';

    allData.food.forEach(food => {
        const isSelected = selectedItems.food.some(item => item.id === food.id);
        const card = createItemCard(food, 'food', {
            title: food.name,
            subtitle: food.type,
            rating: food.rating,
            extra: food.avgPrice,
            image: food.image
        }, isSelected);
        grid.appendChild(card);
    });
}

// 渲染酒店数据
function renderHotels() {
    const grid = document.getElementById('hotels-grid');
    grid.innerHTML = '';

    allData.hotels.forEach(hotel => {
        const isSelected = selectedItems.hotels.some(item => item.id === hotel.id);
        const card = createItemCard(hotel, 'hotels', {
            title: hotel.name,
            subtitle: hotel.location,
            rating: hotel.rating,
            extra: hotel.price,
            image: hotel.image
        }, isSelected);
        grid.appendChild(card);
    });
}

// 渲染交通数据
function renderTransport() {
    const grid = document.getElementById('transport-grid');
    grid.innerHTML = '';

    allData.transport.forEach(transport => {
        const isSelected = selectedItems.transport.some(item => item.id === transport.id);
        const card = createItemCard(transport, 'transport', {
            title: transport.name,
            subtitle: `${transport.type} - ${transport.duration}`,
            rating: transport.time,
            extra: transport.price,
            image: transport.image
        }, isSelected);
        grid.appendChild(card);
    });
}

// 创建项目卡片
function createItemCard(item, category, displayData, isSelected) {
    const card = document.createElement('div');
    card.className = `item-card ${isSelected ? 'selected' : ''}`;
    card.dataset.category = category;
    card.dataset.id = item.id;

    card.innerHTML = `
        <img src="${displayData.image}" alt="${displayData.title}" onerror="this.src='/static/placeholder.jpg'">
        <h4>${displayData.title}</h4>
        <p>${displayData.subtitle}</p>
        <p class="rating">${displayData.rating}</p>
        <p class="price">${displayData.extra}</p>
    `;

    card.addEventListener('click', () => toggleSelection(item, category));
    return card;
}

// 切换选择状态
function toggleSelection(item, category) {
    const index = selectedItems[category].findIndex(selected => selected.id === item.id);
    
    if (index === -1) {
        // 添加到选择列表
        selectedItems[category].push(item);
    } else {
        // 从选择列表移除
        selectedItems[category].splice(index, 1);
    }

    // 更新UI
    updateItemCardSelection(item.id, category);
    updateCartDisplay();
}

// 更新项目卡片选择状态
function updateItemCardSelection(itemId, category) {
    const card = document.querySelector(`[data-category="${category}"][data-id="${itemId}"]`);
    if (card) {
        const isSelected = selectedItems[category].some(item => item.id === itemId);
        if (isSelected) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    }
}

// 更新购物车显示
function updateCartDisplay() {
    const cartContent = document.getElementById('cart-content');
    const cartCount = document.querySelector('.cart-count');
    const generateBtn = document.querySelector('.generate-btn');

    // 计算总选择数量
    const totalCount = Object.values(selectedItems).reduce((total, items) => total + items.length, 0);
    cartCount.textContent = `${totalCount} 项`;

    // 检查是否每个类别都有选择
    const hasAllCategories = Object.values(selectedItems).every(items => items.length > 0);
    generateBtn.disabled = !hasAllCategories;

    if (totalCount === 0) {
        cartContent.innerHTML = `
            <div class="empty-cart">
                <i>🛒</i>
                <p>请从左侧选择项目</p>
            </div>
        `;
        return;
    }

    // 渲染购物车内容
    let cartHTML = '';
    
    if (selectedItems.attractions.length > 0) {
        cartHTML += renderCartCategory('🏞️ 景点', selectedItems.attractions, 'attractions');
    }
    
    if (selectedItems.food.length > 0) {
        cartHTML += renderCartCategory('🍜 美食', selectedItems.food, 'food');
    }
    
    if (selectedItems.hotels.length > 0) {
        cartHTML += renderCartCategory('🏨 酒店', selectedItems.hotels, 'hotels');
    }
    
    if (selectedItems.transport.length > 0) {
        cartHTML += renderCartCategory('🚄 交通', selectedItems.transport, 'transport');
    }

    cartContent.innerHTML = `<div class="cart-categories">${cartHTML}</div>`;
}

// 渲染购物车分类
function renderCartCategory(title, items, category) {
    let itemsHTML = items.map(item => `
        <div class="cart-item">
            <span class="cart-item-name">${getItemDisplayName(item, category)}</span>
            <button class="remove-btn" onclick="removeFromCart('${item.id}', '${category}')">移除</button>
        </div>
    `).join('');

    return `
        <div class="cart-category">
            <h4>${title}</h4>
            ${itemsHTML}
        </div>
    `;
}

// 获取项目显示名称
function getItemDisplayName(item, category) {
    switch(category) {
        case 'attractions':
            return item.name;
        case 'food':
            return item.name;
        case 'hotels':
            return item.name;
        case 'transport':
            return item.name;
        default:
            return item.name;
    }
}

// 从购物车移除项目
function removeFromCart(itemId, category) {
    const index = selectedItems[category].findIndex(item => item.id === itemId);
    if (index !== -1) {
        selectedItems[category].splice(index, 1);
        updateItemCardSelection(itemId, category);
        updateCartDisplay();
    }
}

// 生成推荐方案
async function generateRecommendations() {
    // 检查是否每个类别都有选择
    const categories = ['attractions', 'food', 'hotels', 'transport'];
    for (let category of categories) {
        if (selectedItems[category].length === 0) {
            alert(`请至少选择一个${getCategoryName(category)}`);
            return;
        }
    }

    // 显示加载动画
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.style.display = 'flex';

    try {
        const response = await fetch('/api/generate_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                selectedItems: selectedItems
            })
        });

        if (!response.ok) {
            throw new Error('生成推荐失败');
        }

        const data = await response.json();
        displayRecommendations(data.recommendations);
        
        // 滚动到推荐区域
        document.getElementById('recommendations-section').scrollIntoView({
            behavior: 'smooth'
        });

    } catch (error) {
        console.error('生成推荐失败:', error);
        alert('生成推荐失败，请重试');
    } finally {
        // 隐藏加载动画
        loadingOverlay.style.display = 'none';
    }
}

// 获取分类中文名称
function getCategoryName(category) {
    const names = {
        'attractions': '景点',
        'food': '美食',
        'hotels': '酒店',
        'transport': '交通'
    };
    return names[category] || category;
}

// 显示推荐方案
function displayRecommendations(recommendations) {
    const recommendationsSection = document.getElementById('recommendations-section');
    const recommendationsList = document.getElementById('recommendations-list');

    recommendationsList.innerHTML = '';

    recommendations.forEach((rec, index) => {
        const recCard = createRecommendationCard(rec, index + 1);
        recommendationsList.appendChild(recCard);
    });

    recommendationsSection.style.display = 'block';
}

// 创建推荐卡片
function createRecommendationCard(recommendation, number) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';

    const categoriesHTML = renderRecommendationCategories(recommendation.items);

    card.innerHTML = `
        <div class="recommendation-header">
            <div class="recommendation-number">${number}</div>
            <h3 class="recommendation-title">${recommendation.title}</h3>
        </div>
        
        <div class="recommendation-content">
            ${categoriesHTML}
        </div>
        
        <div class="recommendation-reason">
            <h5>💡 推荐理由</h5>
            <p>${recommendation.reason}</p>
        </div>
    `;

    return card;
}

// 渲染推荐分类内容
function renderRecommendationCategories(items) {
    let html = '';

    if (items.attractions && items.attractions.length > 0) {
        html += createRecommendationCategory('🏞️ 景点', items.attractions, 'attractions');
    }

    if (items.food && items.food.length > 0) {
        html += createRecommendationCategory('🍜 美食', items.food, 'food');
    }

    if (items.hotels && items.hotels.length > 0) {
        html += createRecommendationCategory('🏨 酒店', items.hotels, 'hotels');
    }

    if (items.transport && items.transport.length > 0) {
        html += createRecommendationCategory('🚄 交通', items.transport, 'transport');
    }

    return html;
}

// 创建推荐分类
function createRecommendationCategory(title, items, category) {
    const itemsList = items.map(item => `
        <li>${getRecommendationItemDisplay(item, category)}</li>
    `).join('');

    return `
        <div class="recommendation-item">
            <h5>${title}</h5>
            <ul>
                ${itemsList}
            </ul>
        </div>
    `;
}

// 获取推荐项目显示文本
function getRecommendationItemDisplay(item, category) {
    switch(category) {
        case 'attractions':
            return `${item.name} - ${item.rating}`;
        case 'food':
            return `${item.name} - ${item.avgPrice}`;
        case 'hotels':
            return `${item.name} - ${item.price}`;
        case 'transport':
            return `${item.name} - ${item.price}`;
        default:
            return item.name;
    }
}