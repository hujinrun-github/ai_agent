import requests
import json
import os
import re

def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status() 
        # 解析返回的JSON数据
        data = response.json()
        
        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        # 格式化成自然语言返回
        return f"{city}当前天气:{weather_desc}，气温{temp_c}摄氏度"
        
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"



def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用搜索并返回景点推荐。
    """
    # 构造查询参数
    query = f"{city} {weather} 天气 旅游景点 推荐攻略"

    try:
        # 使用DuckDuckGo Instant Answer API (免费且不需要API key)
        url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=0"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 尝试获取即时答案
        if data.get('AbstractText'):
            return f"📍 {city}\n\n{data['AbstractText']}"

        # 如果没有摘要，尝试相关话题
        if data.get('RelatedTopics'):
            results = []
            for topic in data['RelatedTopics'][:5]:  # 只取前5个结果
                if 'Text' in topic:
                    # 清理HTML标签
                    text = re.sub(r'<[^>]+>', '', topic['Text'])
                    results.append(f"• {text}")

            if results:
                return f"🏞️ {city}景点推荐:\n\n" + "\n\n".join(results)

        # 回退到预设推荐
        fallback_recommendations = {
            "北京": [
                "故宫博物院 - 皇家宫殿建筑群，历史文化厚重",
                "颐和园 - 清代皇家园林，景色优美",
                "长城 - 世界文化遗产，不到长城非好汉",
                "天坛公园 - 明清皇帝祭天的场所"
            ],
            "上海": [
                "外滩 - 上海标志性景观带",
                "东方明珠塔 - 上海地标建筑",
                "豫园 - 明代私家园林",
                "田子坊 - 创意文化街区"
            ],
            "广州": [
                "广州塔 - 小蛮腰城市地标",
                "陈家祠 - 岭南建筑艺术瑰宝",
                "白云山 - 南粤名山，空气清新",
                "长隆旅游度假区 - 综合主题公园"
            ]
        }

        if city in fallback_recommendations:
            return f"🏞️ {city}推荐景点:\n\n" + "\n\n".join(fallback_recommendations[city])
        else:
            return f"🏞️ {city}通用推荐:\n\n在任何天气下，都建议参观当地的博物馆、历史古迹和特色街区，体验当地文化。"

    except Exception as e:
        return f"抱歉，获取景点推荐时遇到问题: {e}\n\n建议您可以查询当地旅游官网或使用其他地图应用获取最新信息。"

# 将所有工具函数放入一个字典，方便后续调用
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}