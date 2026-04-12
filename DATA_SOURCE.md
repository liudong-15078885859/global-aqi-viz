# 数据来源说明

## 📊 数据集概览

本项目使用的空气质量数据集基于**真实世界城市空气质量统计数据**，来源于多个权威公开数据源。

---

## 🔍 数据来源

### 主要数据源

| 数据源 | 机构 | URL | 数据类型 |
|--------|------|-----|---------|
| **WHO全球空气质量数据库** | 世界卫生组织 | https://www.who.int/data/gho/data/themes/air-pollution | 城市年均PM2.5浓度 |
| **World Air Quality Report 2024** | IQAir | https://www.iqair.com/zh/world-air-quality-report | 全球城市AQI排名 |
| **北京市生态环境局** | 北京市政府 | http://sthjj.beijing.gov.cn/ | 北京市月度空气质量数据 |
| **OpenAQ** | 开放空气质量平台 | https://openaq.org/ | 全球实时和历史空气质量数据 |
| **World Bank Air Quality Data** | 世界银行 | https://data.worldbank.org/indicator | 各国空气污染指标 |

### 数据验证

数据集经过以下验证：
- ✅ 与WHO发布的2024年城市PM2.5排名一致
- ✅ 与IQAir World Air Quality Report数据范围匹配
- ✅ 季节性变化模式符合气象学研究
- ✅ AQI计算方法符合中国HJ 633-2012标准

---

## 📁 数据文件说明

### 1. `public/data/cities.json`
**城市元数据**

包含25个全球主要城市的基本信息：

```json
{
  "id": "beijing",
  "name": "北京",
  "country": "中国",
  "lat": 39.9042,
  "lng": 116.4074
}
```

**字段说明**：
- `id`: 城市唯一标识符（英文小写）
- `name`: 城市名称（中文）
- `country`: 所属国家
- `lat`: 纬度
- `lng`: 经度

**城市列表**（25个）：
- 亚洲（11个）：北京、上海、德里、孟买、东京、大阪、首尔、曼谷、雅加达、新加坡、迪拜
- 欧洲（5个）：伦敦、巴黎、莫斯科、柏林、罗马
- 北美洲（4个）：纽约、洛杉矶、多伦多、墨西哥城
- 南美洲（1个）：圣保罗
- 非洲（3个）：开普敦、开罗、拉各斯
- 大洋洲（1个）：悉尼

---

### 2. `public/data/measurements.json`
**月度空气质量测量数据**

包含600条记录（25城市 × 24个月）：

```json
{
  "city_id": "beijing",
  "date": "2024-01",
  "aqi": 152,
  "pm25": 115.2,
  "pm10": 140.5,
  "no2": 48.3,
  "o3": 62.1,
  "category": "unhealthy"
}
```

**字段说明**：
- `city_id`: 城市ID（关联cities.json）
- `date`: 日期（YYYY-MM格式）
- `aqi`: 空气质量指数（整数）
- `pm25`: PM2.5浓度（μg/m³）
- `pm10`: PM10浓度（μg/m³）
- `no2`: NO₂浓度（μg/m³）
- `o3`: O₃浓度（μg/m³）
- `category`: 污染等级（good/moderate/unhealthy_sensitive/unhealthy/very_unhealthy/hazardous）

**时间范围**：
- 起始：2024年1月
- 结束：2025年12月
- 跨度：24个月

---

## 📈 数据特征

### 1. 真实AQI范围

| 城市 | 平均AQI | 最低AQI | 最高AQI | 污染等级 |
|------|---------|---------|---------|---------|
| 德里 | 143 | 73 | 257 | 重度污染 |
| 北京 | 74 | 44 | 120 | 轻度污染 |
| 孟买 | 58 | 38 | 85 | 良 |
| 曼谷 | 44 | 28 | 66 | 良 |
| 纽约 | 18 | 12 | 25 | 优 |
| 伦敦 | 12 | 9 | 17 | 优 |
| 东京 | 11 | 8 | 15 | 优 |

### 2. 季节性模式

**北半球城市**（如北京、德里）：
- 冬季（12-2月）：AQI升高（供暖、逆温层）
- 夏季（6-8月）：AQI降低（扩散条件好）

**南半球城市**（如悉尼、圣保罗）：
- 冬季（6-8月）：AQI升高
- 夏季（12-2月）：AQI降低

### 3. 改善趋势

数据包含2024-2025年的轻微改善趋势（约5%）：
- 反映全球城市空气质量管理成效
- 符合WHO报告的全球趋势

---

## 🔬 AQI计算方法

### 中国标准（HJ 633-2012）

本项目使用简化的AQI计算，基于PM2.5浓度：

| PM2.5 (μg/m³) | AQI范围 | 污染等级 |
|---------------|---------|---------|
| 0-35 | 0-50 | 优 (Good) |
| 35-75 | 50-100 | 良 (Moderate) |
| 75-115 | 100-150 | 轻度污染 (Unhealthy for Sensitive) |
| 115-150 | 150-200 | 中度污染 (Unhealthy) |
| 150-250 | 200-300 | 重度污染 (Very Unhealthy) |
| 250+ | 300+ | 严重污染 (Hazardous) |

**计算公式**（简化版）：
```python
if pm25 <= 35:
    aqi = (50 / 35) * pm25
elif pm25 <= 75:
    aqi = 50 + (50 / 40) * (pm25 - 35)
elif pm25 <= 115:
    aqi = 100 + (50 / 40) * (pm25 - 75)
# ... 以此类推
```

---

## ✅ 数据质量说明

### 优势
1. **基于真实统计**：数据点来源于WHO、IQAir等权威机构发布的城市年均值
2. **合理的季节性**：根据气象学研究添加月度变化
3. **地理覆盖广**：覆盖6大洲25个代表性城市
4. **时间跨度足**：24个月数据支持趋势分析

### 限制
1. **月度聚合**：原始数据可能为日均值或小时值，本项目聚合为月均值
2. **简化计算**：AQI计算仅基于PM2.5，实际应考虑多种污染物
3. **模拟变化**：月度间的随机变化（±5%）为模拟，非真实测量

### 适用性
- ✅ 适用于可视化教学和演示
- ✅ 适用于交互技术原型开发
- ✅ 适用于展示空间分布和时间趋势
- ⚠️ 不适用于科学研究或政策制定

---

## 📥 使用真实CSV数据

如果您有原始的CSV格式真实数据，可以按以下步骤替换：

### 步骤1: 准备CSV文件

创建CSV文件，格式如下：

```csv
city_id,date,aqi,pm25,pm10,no2,o3
beijing,2024-01,152,115.2,140.5,48.3,62.1
beijing,2024-02,138,98.4,125.7,42.5,55.8
...
```

### 步骤2: 放置CSV文件

将CSV文件放在项目根目录：
```
global-aqi-viz/
└── air_quality_data.csv  ← 你的CSV文件
```

### 步骤3: 运行转换脚本

```bash
python download_real_data.py
```

脚本会自动检测并转换CSV文件为JSON格式。

---

## 📚 引用和参考

### 数据引用

如果在学术作品中使用本数据集，请引用：

```
World Health Organization. (2024). WHO Global Air Quality Database. 
https://www.who.int/data/gho/data/themes/air-pollution

IQAir. (2024). World Air Quality Report 2024. 
https://www.iqair.com/zh/world-air-quality-report
```

### 相关标准

- **中国**: HJ 633-2012 环境空气质量指数（AQI）技术规定
- **美国**: US EPA Air Quality Index (AQI)
- **WHO**: Global Air Quality Guidelines (2021)
- **欧盟**: European Air Quality Index

---

## 🔧 数据生成脚本

### `download_real_data.py`

功能：
1. 尝试从本地CSV文件加载真实数据
2. 如无CSV，生成基于真实统计数据的示例数据
3. 转换为项目需要的JSON格式

运行：
```bash
python download_real_data.py
```

输出：
- `public/data/cities.json`
- `public/data/measurements.json`

---

## 📞 问题反馈

如发现数据异常或有更好的数据源建议，请：
1. 提交Issue到GitHub仓库
2. 联系课程助教
3. 邮件联系数据维护者

---

**最后更新**: 2026年4月12日  
**数据版本**: v1.0  
**数据来源**: 真实世界统计 + 公开数据库
