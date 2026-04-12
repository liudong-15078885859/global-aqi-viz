import json
import random
from datetime import datetime

# City profiles with base AQI levels and seasonal patterns
city_profiles = {
    "beijing": {"base": 120, "seasonal": 40, "pm25_ratio": 0.75, "pm10_ratio": 0.9, "no2_base": 45, "o3_base": 65},
    "shanghai": {"base": 95, "seasonal": 30, "pm25_ratio": 0.7, "pm10_ratio": 0.85, "no2_base": 40, "o3_base": 70},
    "delhi": {"base": 180, "seasonal": 80, "pm25_ratio": 0.8, "pm10_ratio": 1.1, "no2_base": 55, "o3_base": 50},
    "mumbai": {"base": 110, "seasonal": 35, "pm25_ratio": 0.65, "pm10_ratio": 0.95, "no2_base": 42, "o3_base": 68},
    "newyork": {"base": 55, "seasonal": 15, "pm25_ratio": 0.5, "pm10_ratio": 0.6, "no2_base": 35, "o3_base": 75},
    "losangeles": {"base": 65, "seasonal": 20, "pm25_ratio": 0.55, "pm10_ratio": 0.65, "no2_base": 38, "o3_base": 85},
    "london": {"base": 50, "seasonal": 12, "pm25_ratio": 0.48, "pm10_ratio": 0.58, "no2_base": 32, "o3_base": 72},
    "paris": {"base": 58, "seasonal": 14, "pm25_ratio": 0.52, "pm10_ratio": 0.62, "no2_base": 36, "o3_base": 73},
    "tokyo": {"base": 45, "seasonal": 10, "pm25_ratio": 0.45, "pm10_ratio": 0.55, "no2_base": 30, "o3_base": 78},
    "osaka": {"base": 48, "seasonal": 12, "pm25_ratio": 0.47, "pm10_ratio": 0.57, "no2_base": 31, "o3_base": 76},
    "moscow": {"base": 65, "seasonal": 25, "pm25_ratio": 0.55, "pm10_ratio": 0.68, "no2_base": 38, "o3_base": 65},
    "sydney": {"base": 35, "seasonal": 10, "pm25_ratio": 0.35, "pm10_ratio": 0.45, "no2_base": 22, "o3_base": 82},
    "capetown": {"base": 42, "seasonal": 12, "pm25_ratio": 0.4, "pm10_ratio": 0.5, "no2_base": 25, "o3_base": 80},
    "saopaulo": {"base": 75, "seasonal": 20, "pm25_ratio": 0.6, "pm10_ratio": 0.72, "no2_base": 40, "o3_base": 70},
    "mexicocity": {"base": 95, "seasonal": 30, "pm25_ratio": 0.68, "pm10_ratio": 0.85, "no2_base": 45, "o3_base": 75},
    "cairo": {"base": 105, "seasonal": 35, "pm25_ratio": 0.72, "pm10_ratio": 0.95, "no2_base": 42, "o3_base": 68},
    "lagos": {"base": 85, "seasonal": 25, "pm25_ratio": 0.65, "pm10_ratio": 0.82, "no2_base": 35, "o3_base": 72},
    "seoul": {"base": 72, "seasonal": 25, "pm25_ratio": 0.58, "pm10_ratio": 0.7, "no2_base": 38, "o3_base": 70},
    "bangkok": {"base": 88, "seasonal": 28, "pm25_ratio": 0.66, "pm10_ratio": 0.8, "no2_base": 40, "o3_base": 73},
    "jakarta": {"base": 92, "seasonal": 25, "pm25_ratio": 0.68, "pm10_ratio": 0.85, "no2_base": 38, "o3_base": 71},
    "singapore": {"base": 52, "seasonal": 15, "pm25_ratio": 0.48, "pm10_ratio": 0.58, "no2_base": 28, "o3_base": 78},
    "berlin": {"base": 48, "seasonal": 12, "pm25_ratio": 0.46, "pm10_ratio": 0.56, "no2_base": 30, "o3_base": 74},
    "rome": {"base": 55, "seasonal": 15, "pm25_ratio": 0.5, "pm10_ratio": 0.6, "no2_base": 33, "o3_base": 76},
    "toronto": {"base": 48, "seasonal": 14, "pm25_ratio": 0.46, "pm10_ratio": 0.56, "no2_base": 30, "o3_base": 76},
    "dubai": {"base": 78, "seasonal": 22, "pm25_ratio": 0.62, "pm10_ratio": 0.88, "no2_base": 35, "o3_base": 82}
}

def get_seasonal_factor(month, city_id):
    """Generate seasonal variation - winter typically worse for northern hemisphere"""
    # Northern hemisphere: worse in winter (Dec-Feb), better in summer (Jun-Aug)
    # Southern hemisphere: opposite
    southern_hemisphere = city_id in ["sydney", "capetown", "saopaulo"]
    
    if southern_hemisphere:
        # Reverse seasons
        if month in [6, 7, 8]:  # Winter
            return 1.3
        elif month in [12, 1, 2]:  # Summer
            return 0.8
        else:
            return 1.0
    else:
        # Northern hemisphere
        if month in [12, 1, 2]:  # Winter
            return 1.3
        elif month in [6, 7, 8]:  # Summer
            return 0.7
        else:
            return 1.0

def generate_measurements():
    measurements = []
    
    for city_id, profile in city_profiles.items():
        for year in [2024, 2025]:
            for month in range(1, 13):
                date_str = f"{year}-{month:02d}"
                
                # Calculate AQI with seasonal variation and some randomness
                seasonal_factor = get_seasonal_factor(month, city_id)
                noise = random.uniform(-0.1, 0.1)
                aqi = int(profile["base"] * seasonal_factor * (1 + noise))
                aqi = max(20, min(350, aqi))  # Clamp between 20-350
                
                # Calculate pollutants based on AQI
                pm25 = round(aqi * profile["pm25_ratio"] * random.uniform(0.9, 1.1), 1)
                pm10 = round(aqi * profile["pm10_ratio"] * random.uniform(0.9, 1.1), 1)
                no2 = round(profile["no2_base"] * seasonal_factor * random.uniform(0.85, 1.15), 1)
                o3 = round(profile["o3_base"] * (2 - seasonal_factor) * random.uniform(0.9, 1.1), 1)
                
                # Determine category
                if aqi <= 50:
                    category = "good"
                elif aqi <= 100:
                    category = "moderate"
                elif aqi <= 150:
                    category = "unhealthy_sensitive"
                elif aqi <= 200:
                    category = "unhealthy"
                elif aqi <= 300:
                    category = "very_unhealthy"
                else:
                    category = "hazardous"
                
                measurements.append({
                    "city_id": city_id,
                    "date": date_str,
                    "aqi": aqi,
                    "pm25": pm25,
                    "pm10": pm10,
                    "no2": no2,
                    "o3": o3,
                    "category": category
                })
    
    return measurements

# Generate and save data
random.seed(42)  # For reproducibility
data = generate_measurements()

with open('public/data/measurements.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Generated {len(data)} measurement records for {len(city_profiles)} cities")
print(f"Date range: 2024-01 to 2025-12")
print(f"Sample record: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
