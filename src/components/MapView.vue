<template>
  <div class="relative w-full h-full">
    <svg ref="svgRef" class="w-full h-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"></svg>
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-500 mb-4"></div>
        <span class="text-white text-lg font-semibold">加载地图数据...</span>
        <div class="text-gray-300 text-sm mt-2">首次加载可能需要几秒钟</div>
      </div>
    </div>
    <!-- 错误提示 -->
    <div v-if="loadError" class="absolute inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div class="text-center bg-white/10 p-6 rounded-2xl border border-white/20 max-w-md">
        <div class="text-4xl mb-3">⚠️</div>
        <div class="text-white text-lg font-semibold mb-2">地图加载失败</div>
        <div class="text-gray-300 text-sm mb-4">{{ loadError }}</div>
        <button 
          @click="retryLoad" 
          class="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
        >
          重试
        </button>
      </div>
    </div>
    <!-- 图例 -->
    <div class="absolute bottom-4 left-4 bg-white/95 backdrop-blur-xl p-4 rounded-xl shadow-2xl border border-white/30 text-xs transition-all duration-300 hover:shadow-purple-500/30">
      <div class="font-bold mb-2 text-gray-800 text-sm flex items-center gap-2">
        <span class="text-lg">🎨</span>
        <span>AQI 等级</span>
      </div>
      <div v-for="item in legendItems" :key="item.label" class="flex items-center gap-3 mb-2 hover:transform hover:scale-105 transition-transform">
        <div class="w-5 h-5 rounded-lg shadow-md" :style="{ backgroundColor: item.color }"></div>
        <span class="text-gray-700 font-medium">{{ item.label }}</span>
      </div>
    </div>
    <!-- 提示信息 -->
    <div v-if="!selectedCityId" class="absolute top-4 left-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-3 rounded-xl shadow-2xl text-sm animate-pulse">
      <div class="flex items-center gap-2">
        <span class="text-xl">💡</span>
        <div>
          <div class="font-semibold">点击地图上的城市查看污染物趋势</div>
          <div class="text-xs mt-1 opacity-90">右键点击可加入对比</div>
        </div>
      </div>
    </div>
    <!-- 高级 Tooltip -->
    <div 
      v-if="tooltip.show" 
      class="absolute pointer-events-none z-50 bg-white/95 backdrop-blur-xl p-4 rounded-xl shadow-2xl border border-purple-200 transition-all duration-200"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="font-bold text-gray-800 text-base mb-2 flex items-center gap-2">
        <span class="text-2xl">{{ tooltip.country === '中国' ? '🇨🇳' : tooltip.country === '美国' ? '🇺🇸' : '🌍' }}</span>
        <span>{{ tooltip.cityName }}</span>
      </div>
      <div class="text-xs text-gray-600 mb-2">{{ tooltip.country }}</div>
      <div class="flex items-center gap-3 mb-2">
        <div class="text-2xl font-bold" :style="{ color: tooltip.color }">{{ tooltip.avgAqi.toFixed(1) }}</div>
        <div class="text-xs px-2 py-1 rounded-lg text-white font-semibold" :style="{ backgroundColor: tooltip.color }">
          {{ tooltip.level }}
        </div>
      </div>
      <div class="text-xs text-gray-500 border-t pt-2 mt-2">
        <div class="flex items-center gap-1">
          <span>👈</span>
          <span>左键点击查看详情</span>
        </div>
        <div class="flex items-center gap-1 mt-1">
          <span>👉</span>
          <span>右键点击加入对比</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import { useData } from '../composables/useData'

const {
  cities,
  worldGeoJson,
  loading,
  cityAvgAqi,
  mapTransform,
  selectedCityId,
  comparedCityId,
  hoveredCityId,
  getAqiColor,
  getCityById,
  loadData
} = useData()

const svgRef = ref(null)
const loadError = ref(null)
let width = 0, height = 0
let projection, path, zoomBehavior
let gMap, gCities
let resizeObserver

const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  cityName: '',
  country: '',
  avgAqi: 0,
  color: '',
  level: ''
})

const legendItems = [
  { label: '优 (0-50)', color: '#00E400' },
  { label: '良 (51-100)', color: '#FFFF00' },
  { label: '轻度污染 (101-150)', color: '#FF7E00' },
  { label: '中度污染 (151-200)', color: '#FF0000' },
  { label: '重度污染 (201-300)', color: '#8F3F97' },
  { label: '严重污染 (300+)', color: '#7E0023' }
]

function getAqiLevel(aqi) {
  if (aqi <= 50) return '优'
  if (aqi <= 100) return '良'
  if (aqi <= 150) return '轻度污染'
  if (aqi <= 200) return '中度污染'
  if (aqi <= 300) return '重度污染'
  return '严重污染'
}

// 初始化地图投影
function initProjection() {
  const svg = d3.select(svgRef.value)
  const bounds = svgRef.value.getBoundingClientRect()
  width = bounds.width
  height = bounds.height
  
  projection = d3.geoMercator()
    .scale(width / 6.5)
    .translate([width / 2, height / 1.5])
  
  path = d3.geoPath().projection(projection)
  
  // 缩放行为
  zoomBehavior = d3.zoom()
    .scaleExtent([0.5, 8])
    .on('zoom', (event) => {
      const { transform } = event
      gMap.attr('transform', transform)
      gCities.attr('transform', transform)
      mapTransform.value = transform
    })
  
  svg.call(zoomBehavior)
}

// 绘制世界地图
function drawMap() {
  if (!worldGeoJson.value || !svgRef.value) return
  
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  
  // 创建地图组
  gMap = svg.append('g')
  gCities = svg.append('g')
  
  // 绘制国家边界 (TopoJSON 转换)
  const countries = topojson.feature(worldGeoJson.value, worldGeoJson.value.objects.land)
  gMap.selectAll('path')
    .data(countries.features)
    .enter()
    .append('path')
    .attr('d', path)
    .attr('fill', 'rgba(255, 255, 255, 0.1)')
    .attr('stroke', 'rgba(255, 255, 255, 0.3)')
    .attr('stroke-width', 0.8)
    .attr('filter', 'drop-shadow(0 0 8px rgba(168, 85, 247, 0.3))')
  
  drawCities()
}

// 绘制城市气泡
function drawCities() {
  if (!gCities) return
  
  gCities.selectAll('*').remove()
  
  const cityEntries = Array.from(cityAvgAqi.value.entries())
  
  // 添加污染粒子效果
  drawPollutionParticles(cityEntries)
  
  cityEntries.forEach(([cityId, { avg }]) => {
    const city = getCityById(cityId)
    if (!city) return
    
    const [x, y] = projection([city.lng, city.lat])
    if (!isNaN(x) && !isNaN(y)) {
      const color = getAqiColor(avg)
      const radius = Math.max(4, Math.min(15, avg / 15))
      
      // 添加脉冲动画效果
      if (avg > 100) {
        gCities.append('circle')
          .attr('cx', x)
          .attr('cy', y)
          .attr('r', radius)
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 2)
          .attr('opacity', 0.6)
          .transition()
          .duration(2000)
          .ease(d3.easeLinear)
          .attr('r', radius * 2.5)
          .attr('opacity', 0)
          .on('end', function repeat() {
            d3.select(this)
              .attr('r', radius)
              .attr('opacity', 0.6)
              .transition()
              .duration(2000)
              .ease(d3.easeLinear)
              .attr('r', radius * 2.5)
              .attr('opacity', 0)
              .on('end', repeat)
          })
      }
      
      const isSel = selectedCityId.value === cityId
      const isCmp = comparedCityId.value === cityId
      const isHov = hoveredCityId.value === cityId
      if (isSel || isCmp || isHov) {
        gCities.append('circle')
          .attr('cx', x)
          .attr('cy', y)
          .attr('r', radius + (isHov ? 8 : 5))
          .attr('fill', 'none')
          .attr('stroke', isSel ? '#fbbf24' : isCmp ? '#38bdf8' : 'rgba(255,255,255,0.85)')
          .attr('stroke-width', isHov ? 3.5 : 2.5)
          .attr('opacity', 0.95)
          .attr('pointer-events', 'none')
      }

      const circle = gCities.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 0)  // 从0开始动画
        .attr('fill', color)
        .attr('stroke', '#fff')
        .attr('stroke-width', isSel || isCmp ? 3.2 : 2.5)
        .attr('opacity', isHov ? 1 : 0.92)
        .attr('cursor', 'pointer')
        .attr('filter', `drop-shadow(0 0 ${isHov ? 14 : 10}px ${color})`)
      
      // 添加城市名称标签
      if (avg > 80) {  // 只为污染较严重的城市显示标签
        gCities.append('text')
          .attr('x', x)
          .attr('y', y - radius - 8)
          .attr('text-anchor', 'middle')
          .attr('font-size', '11px')
          .attr('fill', 'white')
          .attr('font-weight', 'bold')
          .attr('paint-order', 'stroke')
          .attr('stroke', 'rgba(0, 0, 0, 0.5)')
          .attr('stroke-width', 3)
          .text(city.name)
      }
      
      // 动画展开
      circle.transition()
        .duration(500)
        .delay(Math.random() * 300)
        .attr('r', radius)
      
      // 点击事件
      circle.on('click', (event) => {
        event.stopPropagation()
        if (selectedCityId.value === cityId) {
          selectedCityId.value = null
        } else if (comparedCityId.value && comparedCityId.value !== cityId) {
          // 如果已有对比城市，交换
          comparedCityId.value = selectedCityId.value
          selectedCityId.value = cityId
        } else {
          selectedCityId.value = cityId
        }
      })
      
      // 右键点击设置为对比城市
      circle.on('contextmenu', (event) => {
        event.preventDefault()
        event.stopPropagation()
        if (cityId !== selectedCityId.value) {
          comparedCityId.value = comparedCityId.value === cityId ? null : cityId
        }
      })
      
      // 工具提示 - 鼠标悬停
      circle
        .on('mouseenter', (event) => {
          hoveredCityId.value = cityId
          tooltip.value = {
            show: true,
            x: event.offsetX + 20,
            y: event.offsetY - 20,
            cityName: city.name,
            country: city.country,
            avgAqi: avg,
            color: color,
            level: getAqiLevel(avg)
          }
        })
        .on('mousemove', (event) => {
          tooltip.value.x = event.offsetX + 20
          tooltip.value.y = event.offsetY - 20
        })
        .on('mouseleave', () => {
          if (hoveredCityId.value === cityId) hoveredCityId.value = null
          tooltip.value.show = false
        })
      
      circle.append('title')
        .text(`${city.name} (${city.country})\n平均 AQI: ${avg.toFixed(1)}\n左键点击查看详情\n右键点击加入对比`)
    }
  })
}

// 绘制污染粒子效果
function drawPollutionParticles(cityEntries) {
  const highPollutionCities = cityEntries.filter(([cityId, { avg }]) => avg > 150)
  
  highPollutionCities.forEach(([cityId, { avg }]) => {
    const city = getCityById(cityId)
    if (!city) return
    
    const [x, y] = projection([city.lng, city.lat])
    if (isNaN(x) || isNaN(y)) return
    
    const particleCount = Math.floor(avg / 50) // 污染越严重，粒子越多
    
    for (let i = 0; i < particleCount; i++) {
      const angle = (Math.PI * 2 * i) / particleCount
      const distance = 20 + Math.random() * 30
      const px = x + Math.cos(angle) * distance
      const py = y + Math.sin(angle) * distance
      
      gCities.append('circle')
        .attr('cx', px)
        .attr('cy', py)
        .attr('r', 1 + Math.random() * 2)
        .attr('fill', getAqiColor(avg))
        .attr('opacity', 0)
        .transition()
        .delay(Math.random() * 2000)
        .duration(1500)
        .attr('opacity', 0.4)
        .transition()
        .duration(1500)
        .attr('opacity', 0)
        .on('end', function repeat() {
          d3.select(this)
            .attr('opacity', 0)
            .transition()
            .duration(1500)
            .attr('opacity', 0.4)
            .transition()
            .duration(1500)
            .attr('opacity', 0)
            .on('end', repeat)
        })
    }
  })
}

// 重试加载
function retryLoad() {
  loadError.value = null
  loadData()
}

// 监听加载错误
watch(loading, (val) => {
  if (!val && !worldGeoJson.value) {
    loadError.value = '无法加载地图数据，请检查网络连接或刷新页面重试'
  }
})

// 监听数据与联动状态重绘城市（选中 / 对比 / 排行榜悬停）
watch([cityAvgAqi, selectedCityId, comparedCityId, hoveredCityId], () => {
  drawCities()
}, { deep: true })

// 窗口大小自适应
function setupResizeObserver() {
  if (svgRef.value) {
    resizeObserver = new ResizeObserver(() => {
      if (worldGeoJson.value) {
        initProjection()
        drawMap()
      }
    })
    resizeObserver.observe(svgRef.value)
  }
}

// 重置缩放
function resetZoom() {
  if (zoomBehavior && svgRef.value) {
    d3.select(svgRef.value)
      .transition()
      .duration(750)
      .call(zoomBehavior.transform, d3.zoomIdentity)
  }
}

// 暴露方法给父组件
defineExpose({ resetZoom })

onMounted(() => {
  setupResizeObserver()
  // 等待数据加载
  watch(() => worldGeoJson.value, (val) => {
    if (val) {
      initProjection()
      drawMap()
    }
  }, { immediate: true })
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>
