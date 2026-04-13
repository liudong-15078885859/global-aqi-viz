import { ref, computed } from 'vue'
import * as d3 from 'd3'

// AQI 等级颜色映射
const AQI_COLORS = {
  good: '#00E400',
  moderate: '#FFFF00',
  unhealthy_sensitive: '#FF7E00',
  unhealthy: '#FF0000',
  very_unhealthy: '#8F3F97',
  hazardous: '#7E0023'
}

// 模块级单例状态：各组件共享同一数据源，避免「父组件 loadData、子组件永远 loading」的问题
const cities = ref([])
const measurements = ref([])
const worldGeoJson = ref(null)
const loading = ref(true)

const selectedCountries = ref([])
const timeRange = ref([new Date('2024-01-01'), new Date('2025-12-31')])
const selectedCityId = ref(null)
const comparedCityId = ref(null)
/** 悬停联动：地图 ⟷ 排行榜 同步高亮 */
const hoveredCityId = ref(null)
const mapTransform = ref({ k: 1, x: 0, y: 0 })
const isPlaying = ref(false)
const playInterval = ref(null)

// 数据基础路径 — 兼容本地开发（/）和 GitHub Pages 子目录（/repo-name/）
// Vite 构建时会将 import.meta.env.BASE_URL 替换为 vite.config.js 中 base 的值
const DATA_BASE = (typeof import.meta !== 'undefined' && import.meta.env.BASE_URL) || '/'

function fetchWithTimeout(url, timeoutMs = 10000) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
  return fetch(url, { signal: controller.signal })
    .finally(() => clearTimeout(timeoutId))
}

async function loadData() {
  try {
    loading.value = true

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('数据加载总耗时超过30秒，请检查网络或刷新页面重试')), 30000)
    )

    const [citiesRes, measRes, worldRes] = await Promise.race([
      Promise.all([
        fetchWithTimeout(DATA_BASE + 'data/cities.json', 15000).then(r => {
          if (!r.ok) throw new Error('Failed to load cities data (HTTP ' + r.status + ')')
          return r.json()
        }),
        fetchWithTimeout(DATA_BASE + 'data/measurements.json', 15000).then(r => {
          if (!r.ok) throw new Error('Failed to load measurements data (HTTP ' + r.status + ')')
          return r.json()
        }),
        fetchWithTimeout(DATA_BASE + 'data/world-110m.json', 10000)
          .then(r => {
            if (!r.ok) throw new Error('Failed to load local world map data (HTTP ' + r.status + ')')
            return r.json()
          })
          .catch(async (localErr) => {
            console.warn('本地地图数据加载失败:', localErr.message, '尝试从 CDN 加载...')
            try {
              const cdnRes = await fetchWithTimeout('https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json', 8000)
              if (!cdnRes.ok) throw new Error('CDN returned HTTP ' + cdnRes.status)
              console.log('CDN 地图数据加载成功')
              return cdnRes.json()
            } catch (cdnErr) {
              console.error('CDN 也加载失败:', cdnErr.message)
              throw new Error(
                '地图数据加载失败:\n' +
                '- 本地: ' + localErr.message + '\n' +
                '- CDN: ' + cdnErr.message + '\n\n' +
                '请确保 public/data/world-110m.json 文件存在'
              )
            }
          })
      ]),
      timeoutPromise
    ])

    cities.value = citiesRes
    measurements.value = measRes.map(m => ({
      ...m,
      date: new Date(m.date + '-01')
    }))
    worldGeoJson.value = worldRes

    selectedCountries.value = [...new Set(cities.value.map(c => c.country))]

    console.log('数据加载成功:', {
      cities: cities.value.length,
      measurements: measurements.value.length,
      worldGeoJson: !!worldGeoJson.value,
      worldGeoJsonType: worldGeoJson.value.type
    })
  } catch (e) {
    console.error('数据加载失败:', e)
    let errorMsg = e.message || String(e)
    if (e.name === 'AbortError' || errorMsg.includes('abort') || errorMsg.includes('timeout')) {
      errorMsg = '数据加载超时（网络连接较慢或无法访问）。\n\n可能的原因：\n1. 网络连接不稳定\n2. CDN (jsdelivr.net) 在国内访问受限\n3. 文件路径不正确\n\n请按 F12 打开控制台查看详细错误信息'
    }
    alert('数据加载失败: ' + errorMsg)
  } finally {
    loading.value = false
  }
}

const filteredMeasurements = computed(() => {
  let filtered = measurements.value

  const [start, end] = timeRange.value
  filtered = filtered.filter(m => m.date >= start && m.date <= end)

  if (selectedCountries.value.length > 0) {
    const cityIdsInCountry = cities.value
      .filter(c => selectedCountries.value.includes(c.country))
      .map(c => c.id)
    filtered = filtered.filter(m => cityIdsInCountry.includes(m.city_id))
  }

  return filtered
})

/**
 * 折线图用：时间 + 国家筛选与 filteredMeasurements 一致，但**始终保留**当前主选城与对比城，
 * 否则跨国对比时一方会被国家过滤器裁掉，图上只剩一条线。
 */
const measurementsForCharts = computed(() => {
  const [start, end] = timeRange.value
  let filtered = measurements.value.filter(m => m.date >= start && m.date <= end)

  const pinnedCityIds = new Set(
    [selectedCityId.value, comparedCityId.value]
      .filter(Boolean)
      .map(id => String(id))
  )

  if (selectedCountries.value.length > 0) {
    const cityIdsInCountry = new Set(
      cities.value
        .filter(c => selectedCountries.value.includes(c.country))
        .map(c => String(c.id))
    )
    filtered = filtered.filter(
      m => cityIdsInCountry.has(String(m.city_id)) || pinnedCityIds.has(String(m.city_id))
    )
  }

  return filtered
})

const cityAvgAqi = computed(() => {
  const grouped = d3.group(filteredMeasurements.value, d => d.city_id)
  const result = new Map()
  for (const [cityId, records] of grouped) {
    const avg = d3.mean(records, d => d.aqi)
    const city = cities.value.find(c => c.id === cityId)
    result.set(cityId, { avg, city })
  }
  return result
})

const selectedCityTimeSeries = computed(() => {
  if (selectedCityId.value == null || selectedCityId.value === '') return []
  const sid = String(selectedCityId.value)
  return measurementsForCharts.value
    .filter(m => String(m.city_id) === sid)
    .sort((a, b) => a.date - b.date)
})

const comparedCityTimeSeries = computed(() => {
  if (comparedCityId.value == null || comparedCityId.value === '') return []
  const cid = String(comparedCityId.value)
  return measurementsForCharts.value
    .filter(m => String(m.city_id) === cid)
    .sort((a, b) => a.date - b.date)
})

const pollutants = ['pm25', 'pm10', 'no2', 'o3']

function getAqiColor(aqi) {
  if (aqi <= 50) return AQI_COLORS.good
  if (aqi <= 100) return AQI_COLORS.moderate
  if (aqi <= 150) return AQI_COLORS.unhealthy_sensitive
  if (aqi <= 200) return AQI_COLORS.unhealthy
  if (aqi <= 300) return AQI_COLORS.very_unhealthy
  return AQI_COLORS.hazardous
}

const countryList = computed(() => [...new Set(cities.value.map(c => c.country))].sort())

const timeSparklineData = computed(() => {
  const grouped = d3.group(filteredMeasurements.value, d => d.date.getTime())
  const data = []
  for (const [timestamp, records] of grouped) {
    const avg = d3.mean(records, d => d.aqi)
    data.push({ date: new Date(parseInt(timestamp)), avg })
  }
  return data.sort((a, b) => a.date - b.date)
})

/** 仅按国家过滤、不按时间过滤 — 用于时间轴旁「全景」趋势线 + 当前刷选窗口叠层 */
const measurementsForGlobalSparkline = computed(() => {
  let filtered = measurements.value
  if (selectedCountries.value.length > 0) {
    const cityIds = cities.value
      .filter(c => selectedCountries.value.includes(c.country))
      .map(c => c.id)
    filtered = filtered.filter(m => cityIds.includes(m.city_id))
  }
  return filtered
})

const globalTimeSparklineData = computed(() => {
  const src = measurementsForGlobalSparkline.value
  if (!src.length) return []
  const grouped = d3.group(src, d => d.date.getTime())
  const data = []
  for (const [timestamp, records] of grouped) {
    const avg = d3.mean(records, d => d.aqi)
    data.push({ date: new Date(parseInt(timestamp)), avg })
  }
  return data.sort((a, b) => a.date - b.date)
})

function togglePlay() {
  if (isPlaying.value) {
    clearInterval(playInterval.value)
    isPlaying.value = false
  } else {
    isPlaying.value = true
    const [start, end] = timeRange.value
    const currentDate = new Date(timeRange.value[0])
    const monthStep = 1

    playInterval.value = setInterval(() => {
      currentDate.setMonth(currentDate.getMonth() + monthStep)
      if (currentDate > end) {
        currentDate.setTime(start.getTime())
      }
      const newEnd = new Date(currentDate)
      newEnd.setMonth(newEnd.getMonth() + 2)
      if (newEnd > end) {
        timeRange.value = [new Date(currentDate), new Date(end)]
      } else {
        timeRange.value = [new Date(currentDate), newEnd]
      }
    }, 1000)
  }
}

function stopPlay() {
  if (playInterval.value) {
    clearInterval(playInterval.value)
    isPlaying.value = false
  }
}

function getCityById(id) {
  return cities.value.find(c => c.id === id)
}

export function useData() {
  return {
    cities,
    measurements,
    worldGeoJson,
    loading,
    selectedCountries,
    timeRange,
    selectedCityId,
    comparedCityId,
    hoveredCityId,
    mapTransform,
    isPlaying,
    cityAvgAqi,
    selectedCityTimeSeries,
    comparedCityTimeSeries,
    pollutants,
    countryList,
    timeSparklineData,
    globalTimeSparklineData,
    loadData,
    getAqiColor,
    togglePlay,
    stopPlay,
    getCityById
  }
}
