<template>
  <div class="p-6 bg-gradient-to-br from-white/95 to-white/90 shadow-2xl rounded-2xl border border-white/30 flex flex-wrap gap-6 items-end transition-shadow duration-300 hover:shadow-purple-500/25 [contain:paint]">
    <!-- 国家过滤器 -->
    <div class="flex-1 min-w-48">
      <label class="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
        <span class="text-xl">🌐</span>
        <span>国家/地区 ({{ selectedCountries.length }}/{{ countryList.length }})</span>
      </label>
      <select
        multiple
        v-model="selectedCountriesModel"
        class="w-full p-3 border-2 border-purple-200 rounded-xl text-sm h-32 bg-white/70 backdrop-blur-sm focus:border-purple-500 focus:ring-2 focus:ring-purple-300 transition-all duration-200 cursor-pointer"
        @change="onCountryChange"
      >
        <option v-for="c in countryList" :key="c" :value="c" class="py-2 px-2 hover:bg-purple-100 cursor-pointer">{{ c }}</option>
      </select>
      <div class="text-xs text-gray-600 mt-2 flex items-center gap-1">
        <span>💡</span>
        <span>按住 Ctrl/Cmd 多选，或点击全选/清空按钮</span>
      </div>
      <div class="flex gap-2 mt-3">
        <button @click="selectAllCountries" class="flex-1 text-xs px-3 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 font-medium">✓ 全选</button>
        <button @click="deselectAllCountries" class="flex-1 text-xs px-3 py-2 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg hover:from-gray-600 hover:to-gray-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 font-medium">✗ 清空</button>
      </div>
    </div>
    
    <!-- 时间轴刷选 -->
    <div class="flex-2 min-w-96">
      <div class="flex justify-between items-center mb-2">
        <label class="block text-sm font-semibold text-gray-800 flex items-center gap-2">
          <span class="text-xl">⏱️</span>
          <span>时间范围: {{ formatDate(timeRange[0]) }} - {{ formatDate(timeRange[1]) }}</span>
        </label>
        <button 
          @click="togglePlay" 
          class="px-4 py-2 text-sm rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center gap-2"
          :class="isPlaying ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white' : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white'"
        >
          <span class="text-lg">{{ isPlaying ? '⏸' : '▶' }}</span>
          <span>{{ isPlaying ? '暂停' : '播放' }}</span>
        </button>
      </div>
      <div ref="brushRef" class="w-full h-20 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-2"></div>
      <!-- Sparkline 趋势指示器 -->
      <div class="text-[10px] text-gray-500 mt-1 mb-0.5">全景平均 AQI（紫带 = 当前刷选时间窗，与地图/图表联动）</div>
      <div ref="sparklineRef" class="w-full h-16 mt-1 rounded-lg bg-white/40 border border-purple-100/80"></div>
    </div>
    
    <!-- 重置按钮 -->
    <button @click="resetAll" class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl hover:from-purple-600 hover:to-pink-600 text-sm transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 text-white font-semibold flex items-center gap-2">
      <span class="text-lg">🔄</span>
      <span>重置视图</span>
    </button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import * as d3 from 'd3'
import { useData } from '../composables/useData'

const {
  measurements,
  timeRange,
  selectedCountries,
  countryList,
  isPlaying,
  globalTimeSparklineData,
  togglePlay,
  stopPlay
} = useData()

const brushRef = ref(null)
const sparklineRef = ref(null)
const selectedCountriesModel = computed({
  get: () => selectedCountries.value,
  set: (val) => { selectedCountries.value = val }
})

function formatDate(d) {
  return d3.timeFormat('%Y-%m')(d)
}

function selectAllCountries() {
  console.log('Selecting all countries')
  selectedCountries.value = countryList.value
}

function deselectAllCountries() {
  console.log('Deselecting all countries')
  selectedCountries.value = []
}

function onCountryChange(event) {
  console.log('Country selection changed:', selectedCountries.value)
}

function initBrush() {
  if (!brushRef.value || !measurements.value.length) {
    console.log('Brush init skipped:', { hasRef: !!brushRef.value, hasData: measurements.value.length })
    return
  }
  
  console.log('Initializing brush with', measurements.value.length, 'measurements')
  
  const margin = { left: 10, right: 10 }
  const width = brushRef.value.clientWidth - margin.left - margin.right
  const height = 60  // 增加高度以便交互
  
  d3.select(brushRef.value).selectAll('*').remove()
  
  const svg = d3.select(brushRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height)
    .style('cursor', 'crosshair')
    .append('g')
    .attr('transform', `translate(${margin.left},0)`)
  
  // 计算时间范围
  const dates = measurements.value.map(d => d.date)
  const extent = d3.extent(dates)
  
  console.log('Date extent:', extent)
  
  const x = d3.scaleTime()
    .domain(extent)
    .range([0, width])
  
  // 背景条 - 更明显的背景
  svg.append('rect')
    .attr('width', width)
    .attr('height', height - 15)
    .attr('fill', '#e5e7eb')
    .attr('rx', 6)
    .attr('stroke', '#9ca3af')
    .attr('stroke-width', 1)
  
  // 添加月份刻度
  svg.append('g')
    .attr('transform', `translate(0,${height - 15})`)
    .call(d3.axisBottom(x).ticks(12).tickFormat(d3.timeFormat('%y/%m')).tickSize(4))
    .selectAll('text')
    .attr('font-size', '9px')
    .attr('fill', '#6b7280')
  
  // Brush - 增强交互
  const brush = d3.brushX()
    .extent([[0, 0], [width, height - 20]])
    .on('brush', (event) => {
      if (event.selection) {
        const [x0, x1] = event.selection
        timeRange.value = [x.invert(x0), x.invert(x1)]
        console.log('Brushing:', timeRange.value)
      }
    })
    .on('end', (event) => {
      if (!event.selection) {
        // 如果清除刷选，重置为默认范围
        timeRange.value = extent
        console.log('Brush cleared, resetting to default')
      } else {
        const [x0, x1] = event.selection
        timeRange.value = [x.invert(x0), x.invert(x1)]
        console.log('Brush ended:', timeRange.value)
      }
    })
  
  const brushG = svg.append('g')
    .attr('class', 'brush')
    .call(brush)
  
  // 设置初始刷选范围
  const defaultSelection = [x(extent[0]), x(extent[1])]
  brushG.call(brush.move, defaultSelection)
  
  // 自定义刷选手柄样式 - 更明显
  brushG.selectAll('.handle')
    .attr('fill', '#8b5cf6')
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .attr('rx', 4)
  
  // 刷选区域样式
  brushG.selectAll('.overlay')
    .style('pointer-events', 'all')
    .style('cursor', 'crosshair')
  
  brushG.selectAll('.selection')
    .attr('fill', '#8b5cf6')
    .attr('fill-opacity', 0.3)
    .attr('stroke', '#7c3aed')
    .attr('stroke-width', 2)
  
  console.log('Brush initialized successfully')
}

// 绘制 Sparkline：全景时间序列 + 当前刷选窗口（多视图协调 / focus+context）
function drawSparkline() {
  if (!sparklineRef.value || !globalTimeSparklineData.value.length) return

  const margin = { left: 8, right: 8, top: 10, bottom: 14 }
  const width = sparklineRef.value.clientWidth - margin.left - margin.right
  const height = sparklineRef.value.clientHeight - margin.top - margin.bottom
  if (width <= 0 || height <= 0) return

  d3.select(sparklineRef.value).selectAll('*').remove()

  const svgRoot = d3.select(sparklineRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .attr('overflow', 'visible')

  const defs = svgRoot.append('defs')
  const gradId = 'spark-grad-' + Math.random().toString(36).slice(2, 9)
  const gradient = defs.append('linearGradient')
    .attr('id', gradId)
    .attr('x1', '0%').attr('y1', '0%')
    .attr('x2', '0%').attr('y2', '100%')

  gradient.append('stop').attr('offset', '0%').attr('stop-color', '#7c3aed').attr('stop-opacity', 0.45)
  gradient.append('stop').attr('offset', '100%').attr('stop-color', '#a78bfa').attr('stop-opacity', 0.06)

  const svg = svgRoot.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const data = globalTimeSparklineData.value
  const x = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([0, width])

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.avg) * 1.08 || 1])
    .nice()
    .range([height, 0])

  const [win0, win1] = timeRange.value
  let xw0 = x(win0)
  let xw1 = x(win1)
  if (xw0 > xw1) [xw0, xw1] = [xw1, xw0]
  xw0 = Math.max(0, xw0)
  xw1 = Math.min(width, xw1)

  svg.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', width)
    .attr('height', height)
    .attr('fill', '#f8fafc')
    .attr('rx', 4)

  if (xw1 > xw0) {
    svg.append('rect')
      .attr('x', xw0)
      .attr('y', 0)
      .attr('width', xw1 - xw0)
      .attr('height', height)
      .attr('fill', '#7c3aed')
      .attr('opacity', 0.22)
      .attr('rx', 3)
  }

  const area = d3.area()
    .x(d => x(d.date))
    .y0(height)
    .y1(d => y(d.avg))
    .curve(d3.curveMonotoneX)

  svg.append('path')
    .datum(data)
    .attr('fill', `url(#${gradId})`)
    .attr('d', area)

  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.avg))
    .curve(d3.curveMonotoneX)

  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', '#5b21b6')
    .attr('stroke-width', 1.8)
    .attr('opacity', 0.85)
    .attr('d', line)

  if (xw1 > xw0) {
    svg.append('line')
      .attr('x1', xw0)
      .attr('x2', xw0)
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#6d28d9')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '3,2')
      .attr('opacity', 0.9)
    svg.append('line')
      .attr('x1', xw1)
      .attr('x2', xw1)
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#6d28d9')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '3,2')
      .attr('opacity', 0.9)
  }

  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(4).tickFormat(d3.timeFormat('%y-%m')))
    .call(g => g.select('.domain').attr('stroke', '#cbd5e1'))
    .selectAll('text')
    .attr('font-size', '8px')
    .attr('fill', '#64748b')
}

function resetAll() {
  selectedCountries.value = countryList.value
  const extent = d3.extent(measurements.value, d => d.date)
  timeRange.value = [extent[0], extent[1]]
  stopPlay()
  // 重置地图缩放（需要调用地图组件的方法）
}

function handleTogglePlay() {
  togglePlay()
}

watch(measurements, (val) => {
  if (val.length) {
    console.log('Measurements loaded, initializing brush and sparkline')
    // 等待 DOM 更新后再初始化
    setTimeout(() => {
      initBrush()
      drawSparkline()
    }, 100)
  }
}, { immediate: true })

watch([globalTimeSparklineData, timeRange], () => {
  drawSparkline()
}, { deep: true })

// 监听时间范围变化
watch(timeRange, (newVal) => {
  console.log('Time range changed:', newVal)
}, { deep: true })

let resizeObs
onMounted(() => {
  resizeObs = new ResizeObserver(() => {
    initBrush()
    drawSparkline()
  })
  if (brushRef.value) resizeObs.observe(brushRef.value)
  if (sparklineRef.value) resizeObs.observe(sparklineRef.value)
})

onUnmounted(() => {
  if (resizeObs) resizeObs.disconnect()
  stopPlay()
})
</script>

<style scoped>
/* 自定义多选框样式 */
select[multiple] option {
  padding: 8px 12px;
  margin: 2px 0;
  border-radius: 6px;
  transition: all 0.2s;
}

select[multiple] option:checked {
  background: linear-gradient(to right, #8b5cf6, #a78bfa) !important;
  color: white !important;
  font-weight: 600;
}

select[multiple] option:hover {
  background-color: #ede9fe !important;
}

/* 刷选区域样式增强 */
:deep(.brush .handle) {
  transition: fill 0.2s;
}

:deep(.brush .handle:hover) {
  fill: #7c3aed !important;
}
</style>
