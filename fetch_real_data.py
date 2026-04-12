"""
从OpenAQ API获取真实空气质量数据
下载并处理为静态JSON文件供前端使用
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time

# 选择25个全球主要城市
CITIES = [
    {"id": "beijing", "name": "北京", "country": "中国", "lat": 39.9042, "lng": 116.4074, "city_param": "Beijing"},
    {"id": "shanghai", "name": "上海", "country": "中国", "lat": 31.2304, "lng": 121.4737, "city_param": "Shanghai"},
    {"id": "delhi", "name": "德里", "country": "印度", "lat": 28.6139, "lng": 77.2090, "city_param": "Delhi"},
    {"id": "mumbai", "name": "孟买", "country": "印度", "lat": 19.0760, "lng": 72.8777, "city_param": "Mumbai"},
    {"id": "newyork", "name": "纽约", "country": "美国", "lat": 40.7128, "lng": -74.0060, "city_param": "New York"},
    {"id": "losangeles", "name": "洛杉矶", "country": "美国", "lat": 34.0522, "lng": -118.2437, "city_param": "Los Angeles"},
    {"id": "london", "name": "伦敦", "country": "英国", "lat": 51.5074, "lng": -0.1278, "city_param": "London"},
    {"id": "paris", "name": "巴黎", "country": "法国", "lat": 48.8566, "lng": 2.3522, "city_param": "Paris"},
    {"id": "tokyo", "name": "东京", "country": "日本", "lat": 35.6895, "lng": 139.6917, "city_param": "Tokyo"},
    {"id": "osaka", "name": "大阪", "country": "日本", "lat": 34.6937, "lng": 135.5023, "city_param": "Osaka"},
    {"id": "moscow", "name": "莫斯科", "country": "俄罗斯", "lat": 55.7558, "lng": 37.6173, "city_param": "Moscow"},
    {"id": "sydney", "name": "悉尼", "country": "澳大利亚", "lat": -33.8688, "lng": 151.2093, "city_param": "Sydney"},
    {"id": "capetown", "name": "开普敦", "country": "南非", "lat": -33.9249, "lng": 18.4241, "city_param": "Cape Town"},
    {"id": "saopaulo", "name": "圣保罗", "country": "巴西", "lat": -23.5505, "lng": -46.6333, "city_param": "Sao Paulo"},
    {"id": "mexicocity", "name": "墨西哥城", "country": "墨西哥", "lat": 19.4326, "lng": -99.1332, "city_param": "Mexico City"},
    {"id": "cairo", "name": "开罗", "country": "埃及", "lat": 30.0444, "lng": 31.2357, "city_param": "Cairo"},
    {"id": "lagos", "name": "拉各斯", "country": "尼日利亚", "lat": 6.5244, "lng": 3.3792, "city_param": "Lagos"},
    {"id": "seoul", "name": "首尔", "country": "韩国", "lat": 37.5665, "lng": 126.9780, "city_param": "Seoul"},
    {"id": "bangkok", "name": "曼谷", "country": "泰国", "lat": 13.7563, "lng": 100.5018, "city_param": "Bangkok"},
    {"id": "jakarta", "name": "雅加达", "country": "印度尼西亚", "lat": -6.2088, "lng": 106.8456, "city_param": "Jakarta"},
    {"id": "singapore", "name": "新加坡", "country": "新加坡", "lat": 1.3521, "lng": 103.8198, "city_param": "Singapore"},
    {"id": "berlin", "name": "柏林", "country": "德国", "lat": 52.5200, "lng": 13.4050, "city_param": "Berlin"},
    {"id": "rome", "name": "罗马", "country": "意大利", "lat": 41.9028, "lng": 12.4964, "city_param": "Rome"},
    {"id": "toronto", "name": "多伦多", "country": "加拿大", "lat": 43.6532, "lng": -79.3832, "city_param": "Toronto"},
    {"id": "dubai", "name": "迪拜", "country": "阿联酋", "lat": 25.2048, "lng": 55.2708, "city_param": "Dubai"}
]

# 污染物参数
PARAMETERS = ["pm25", "pm10", "no2", "o3"]

def fetch_city_data(city, start_date, end_date):
    """从OpenAQ获取单个城市的数据"""
    print(f"正在获取 {city['name']} ({city['city_param']}) 的数据...")
    
    all_measurements = []
    
    for param in PARAMETERS:
        print(f"  - 获取 {param} 数据...")
        
        # OpenAQ API v2
        url = "https://api.openaq.org/v2/measurements"
        
        # 分页获取数据
        page = 1
        limit = 1000  # 每页最大1000条
        
        while True:
            params = {
                "city": city["city_param"],
                "parameter": param,
                "date_from": start_date.isoformat(),
                "date_to": end_date.isoformat(),
                "limit": limit,
                "page": page,
                "order_by": "datetime",
                "sort": "asc"
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("results"):
                    break
                
                all_measurements.extend(data["results"])
                
                # 检查是否还有更多数据
                if len(data["results"]) < limit:
                    break
                
                page += 1
                time.sleep(0.5)  # 避免API限流
                
            except Exception as e:
                print(f"    错误: {e}")
                break
    
    print(f"  ✓ 获取了 {len(all_measurements)} 条原始记录")
    return all_measurements

def aggregate_monthly_data(raw_data):
    """将原始数据聚合为月度平均值"""
    # 按月份组织数据
    monthly_data = defaultdict(lambda: defaultdict(list))
    
    for record in raw_data:
        if not record.get("date") or not record.get("value"):
            continue
        
        # 解析日期
        date_str = record["date"]["utc"][:7]  # 获取 "YYYY-MM"
        value = record["value"]
        parameter = record["parameter"]
        
        monthly_data[date_str][parameter].append(value)
    
    # 计算月度平均值
    aggregated = {}
    for date_str, params in monthly_data.items():
        aggregated[date_str] = {}
        for param, values in params.items():
            if values:
                aggregated[date_str][param] = sum(values) / len(values)
    
    return aggregated

def calculate_aqi(pm25, pm10, no2, o3):
    """简化的AQI计算（基于中国标准）"""
    # 简化的AQI计算，实际应使用完整的分段线性插值
    # 这里使用PM2.5作为主要参考
    if pm25 is None:
        if pm10:
            return int(pm10 * 0.8)
        return 50
    
    # 基于PM2.5的简化AQI
    if pm25 <= 35:
        aqi = (50 / 35) * pm25
    elif pm25 <= 75:
        aqi = 50 + (50 / 40) * (pm25 - 35)
    elif pm25 <= 115:
        aqi = 100 + (50 / 40) * (pm25 - 75)
    elif pm25 <= 150:
        aqi = 150 + (50 / 35) * (pm25 - 115)
    elif pm25 <= 250:
        aqi = 200 + (100 / 100) * (pm25 - 150)
    else:
        aqi = 300 + (200 / 100) * (pm25 - 250)
    
    return int(min(aqi, 500))

def get_category(aqi):
    """根据AQI值获取污染等级"""
    if aqi <= 50:
        return "good"
    elif aqi <= 100:
        return "moderate"
    elif aqi <= 150:
        return "unhealthy_sensitive"
    elif aqi <= 200:
        return "unhealthy"
    elif aqi <= 300:
        return "very_unhealthy"
    else:
        return "hazardous"

def main():
    print("=" * 60)
    print("OpenAQ 真实数据下载工具")
    print("=" * 60)
    
    # 设置时间范围：最近24个月
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 约24个月
    
    print(f"\n时间范围: {start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')}")
    print(f"城市数量: {len(CITIES)}")
    print()
    
    # 保存城市元数据
    cities_metadata = []
    for city in CITIES:
        cities_metadata.append({
            "id": city["id"],
            "name": city["name"],
            "country": city["country"],
            "lat": city["lat"],
            "lng": city["lng"]
        })
    
    # 获取每个城市的数据
    all_measurements = []
    
    for i, city in enumerate(CITIES, 1):
        print(f"\n[{i}/{len(CITIES)}] 处理 {city['name']}...")
        
        # 获取原始数据
        raw_data = fetch_city_data(city, start_date, end_date)
        
        if not raw_data:
            print(f"  ⚠ 未获取到数据，跳过")
            continue
        
        # 聚合为月度数据
        monthly_data = aggregate_monthly_data(raw_data)
        
        # 转换为项目需要的格式
        for date_str, params in sorted(monthly_data.items()):
            pm25 = params.get("pm25")
            pm10 = params.get("pm10")
            no2 = params.get("no2")
            o3 = params.get("o3")
            
            # 计算AQI
            aqi = calculate_aqi(pm25, pm10, no2, o3)
            
            measurement = {
                "city_id": city["id"],
                "date": date_str,
                "aqi": aqi,
                "pm25": round(pm25, 1) if pm25 else None,
                "pm10": round(pm10, 1) if pm10 else None,
                "no2": round(no2, 1) if no2 else None,
                "o3": round(o3, 1) if o3 else None,
                "category": get_category(aqi)
            }
            
            all_measurements.append(measurement)
        
        print(f"  ✓ 生成了 {len(monthly_data)} 条月度记录")
        
        # 避免API限流
        if i < len(CITIES):
            time.sleep(1)
    
    # 保存为JSON文件
    print("\n" + "=" * 60)
    print("保存数据...")
    
    # 保存城市数据
    with open("public/data/cities.json", "w", encoding="utf-8") as f:
        json.dump(cities_metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ 城市数据: public/data/cities.json ({len(cities_metadata)} 个城市)")
    
    # 保存测量数据
    with open("public/data/measurements.json", "w", encoding="utf-8") as f:
        json.dump(all_measurements, f, indent=2, ensure_ascii=False)
    print(f"✓ 测量数据: public/data/measurements.json ({len(all_measurements)} 条记录)")
    
    # 统计数据
    cities_with_data = len(set(m["city_id"] for m in all_measurements))
    date_range = sorted(set(m["date"] for m in all_measurements))
    
    print("\n" + "=" * 60)
    print("数据统计")
    print("=" * 60)
    print(f"有数据的城市: {cities_with_data}/{len(CITIES)}")
    if date_range:
        print(f"日期范围: {date_range[0]} 至 {date_range[-1]}")
    print(f"总记录数: {len(all_measurements)}")
    
    # 显示每个城市的记录数
    print("\n各城市记录数:")
    city_counts = defaultdict(int)
    for m in all_measurements:
        city_counts[m["city_id"]] += 1
    
    for city_id, count in sorted(city_counts.items()):
        city_name = next((c["name"] for c in CITIES if c["id"] == city_id), city_id)
        print(f"  {city_name}: {count} 条")
    
    print("\n" + "=" * 60)
    print("✓ 数据获取完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
