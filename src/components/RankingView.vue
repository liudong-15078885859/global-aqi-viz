<template>
  <div class="w-full h-full min-h-0 p-6 bg-gradient-to-br from-white/95 to-white/90 rounded-2xl shadow-2xl border border-white/30 flex flex-col overflow-hidden transition-shadow duration-300 hover:shadow-purple-500/25 [contain:paint]">
    <div class="flex justify-between items-center mb-4">
      <h3 class="font-bold text-xl flex items-center gap-2">
        <span class="text-2xl">🏆</span>
        <span class="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">城市污染排名</span>
      </h3>
      <div class="flex gap-2">
        <button 
          @click="sortBy = 'aqi'" 
          class="px-3 py-1 text-xs rounded-lg transition-all duration-200 font-semibold"
          :class="sortBy === 'aqi' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
        >
          AQI
        </button>
        <button 
          @click="sortBy = 'pm25'" 
          class="px-3 py-1 text-xs rounded-lg transition-all duration-200 font-semibold"
          :class="sortBy === 'pm25' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
        >
          PM2.5
        </button>
      </div>
    </div>
    
    <div ref="chartRef" class="flex-1 w-full overflow-y-auto"></div>
    
    <div class="mt-3 text-xs text-gray-600 border-t-2 border-purple-200 pt-3 bg-gradient-to-br from-orange-50 to-red-50 p-3 rounded-xl">
      <div class="flex items-center gap-2">
        <span class="text-lg">🔗</span>
        <span>点击条形联动地图与折线图；悬停可与地图<strong class="text-violet-700">双向高亮</strong></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import * as d3 from 'd3'
import { useData } from '../composables/useData'

const {
  cities,
  measurements,
  timeRange,
  selectedCountries,
  selectedCityId,
  comparedCityId,
  hoveredCityId,
  getAqiColor
} = useData()

const chartRef = ref(null)
const sortBy = ref('aqi')

// 计算城市排名数据
const rankingData = computed(() => {
  const filtered = measurements.value.filter(m => {
    const [start, end] = timeRange.value
    return m.date >= start && m.date <= end
  })

  const grouped = d3.group(filtered, d => d.city_id)
  const rankings = []

  for (const [cityId, records] of grouped) {
    const city = cities.value.find(c => c.id === cityId)
    if (!city) continue

    const avgAqi = d3.mean(records, d => d.aqi)
    const avgPm25 = d3.mean(records, d => d.pm25)
    const avgPm10 = d3.mean(records, d => d.pm10)
    const avgNo2 = d3.mean(records, d => d.no2)
    const avgO3 = d3.mean(records, d => d.o3)

    rankings.push({
      cityId,
      cityName: city.name,
      country: city.country,
      avgAqi,
      avgPm25,
      avgPm10,
      avgNo2,
      avgO3
    })
  }

  // 排序
  rankings.sort((a, b) => {
    if (sortBy.value === 'aqi') return b.avgAqi - a.avgAqi
    if (sortBy.value === 'pm25') return b.avgPm25 - a.avgPm25
    return 0
  })

  return rankings.slice(0, 15) // 只显示前15名
})

function drawChart() {
  if (!chartRef.value || !rankingData.value.length) return

  const data = rankingData.value
  const margin = { top: 10, right: 80, bottom: 10, left: 100 }
  const width = chartRef.value.clientWidth - margin.left - margin.right
  const barHeight = 35
  const barPadding = 8
  const height = data.length * (barHeight + barPadding)

  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // X 轴比例尺
  const maxValue = d3.max(data, d => sortBy.value === 'aqi' ? d.avgAqi : d.avgPm25)
  const x = d3.scaleLinear()
    .domain([0, maxValue * 1.1])
    .range([0, width])

  // Y 轴比例尺
  const y = d3.scaleBand()
    .domain(data.map(d => d.cityName))
    .range([0, height])
    .padding(0.2)

  // 绘制条形
  const bars = svg.selectAll('.bar')
    .data(data)
    .enter()
    .append('g')
    .attr('class', 'bar-group')
    .attr('transform', (d, i) => `translate(0, ${i * (barHeight + barPadding)})`)

  // 条形背景
  bars.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', width)
    .attr('height', barHeight)
    .attr('fill', 'rgba(243, 244, 246, 0.5)')
    .attr('rx', 8)

  // 数值条形（与地图 / 折线图联动：选中、对比、悬停）
  bars.append('rect')
    .attr('class', 'rank-value-bar')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', 0)
    .attr('height', barHeight)
    .attr('fill', d => {
      const value = sortBy.value === 'aqi' ? d.avgAqi : d.avgPm25
      return getAqiColor(value)
    })
    .attr('rx', 8)
    .attr('opacity', d => (hoveredCityId.value === d.cityId ? 1 : 0.88))
    .attr('cursor', 'pointer')
    .attr('stroke', d => {
      if (d.cityId === selectedCityId.value) return '#fbbf24'
      if (d.cityId === comparedCityId.value) return '#38bdf8'
      if (d.cityId === hoveredCityId.value) return '#c4b5fd'
      return 'transparent'
    })
    .attr('stroke-width', d => {
      if (d.cityId === selectedCityId.value || d.cityId === comparedCityId.value) return 3
      if (d.cityId === hoveredCityId.value) return 2.5
      return 0
    })
    .on('click', (event, d) => {
      if (selectedCityId.value === d.cityId) {
        selectedCityId.value = null
      } else {
        selectedCityId.value = d.cityId
      }
    })
    .on('mouseenter', (event, d) => {
      hoveredCityId.value = d.cityId
    })
    .on('mouseleave', () => {
      hoveredCityId.value = null
    })
    .transition()
    .duration(550)
    .ease(d3.easeCubicOut)
    .attr('width', d => x(sortBy.value === 'aqi' ? d.avgAqi : d.avgPm25))

  updateBarHighlight()

  // 城市名称
  bars.append('text')
    .attr('x', -10)
    .attr('y', barHeight / 2)
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'middle')
    .attr('font-size', '13px')
    .attr('font-weight', '600')
    .attr('fill', '#374151')
    .text(d => d.cityName)

  // 数值标签
  bars.append('text')
    .attr('x', d => x(sortBy.value === 'aqi' ? d.avgAqi : d.avgPm25) + 8)
    .attr('y', barHeight / 2)
    .attr('dominant-baseline', 'middle')
    .attr('font-size', '14px')
    .attr('font-weight', 'bold')
    .attr('fill', '#1f2937')
    .text(d => {
      const value = sortBy.value === 'aqi' ? d.avgAqi : d.avgPm25
      return value.toFixed(1)
    })

  // 排名徽章
  bars.append('circle')
    .attr('cx', width + 20)
    .attr('cy', barHeight / 2)
    .attr('r', 12)
    .attr('fill', (d, i) => {
      if (i === 0) return '#FFD700'
      if (i === 1) return '#C0C0C0'
      if (i === 2) return '#CD7F32'
      return '#6B7280'
    })
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)

  bars.append('text')
    .attr('x', width + 20)
    .attr('y', barHeight / 2)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .attr('fill', '#fff')
    .text((d, i) => `#${i + 1}`)
}

/** 仅更新描边/透明度，避免地图悬停时整表 remove+重绘触发合成层模糊残影 */
function updateBarHighlight() {
  if (!chartRef.value) return
  const root = d3.select(chartRef.value)
  if (root.select('svg').empty()) return
  const hid = hoveredCityId.value
  const sid = selectedCityId.value
  const cid = comparedCityId.value
  root.selectAll('.bar-group').each(function (d) {
    d3.select(this).select('.rank-value-bar')
      .attr('opacity', hid === d.cityId ? 1 : 0.88)
      .attr('stroke', sid === d.cityId ? '#fbbf24' : cid === d.cityId ? '#38bdf8' : hid === d.cityId ? '#c4b5fd' : 'transparent')
      .attr('stroke-width', sid === d.cityId || cid === d.cityId ? 3 : hid === d.cityId ? 2.5 : 0)
  })
}

watch([rankingData, sortBy, selectedCityId, comparedCityId], drawChart, { deep: true })
watch(hoveredCityId, updateBarHighlight)

let resizeObs
onMounted(() => {
  resizeObs = new ResizeObserver(() => drawChart())
  if (chartRef.value) resizeObs.observe(chartRef.value)
})

onUnmounted(() => {
  if (resizeObs) resizeObs.disconnect()
})
</script>
