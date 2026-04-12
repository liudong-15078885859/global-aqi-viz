<template>
  <div class="w-full h-full min-h-0 overflow-y-auto overflow-x-hidden p-6 bg-gradient-to-br from-white/95 to-white/90 rounded-2xl shadow-2xl border border-white/30 flex flex-col min-h-[320px] transition-shadow duration-300 hover:shadow-purple-500/25">
    <div class="flex justify-between items-center mb-3 flex-shrink-0">
      <h3 class="font-bold text-xl flex items-center gap-2">
        <span class="text-2xl">📊</span>
        <span v-if="selectedCity" class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{{ selectedCity.name }}</span>
        <span v-if="comparedCity" class="text-gray-500"> vs {{ comparedCity.name }}</span>
        <span v-if="!selectedCity" class="text-gray-400">点击地图上的城市查看详情</span>
      </h3>
      <div class="flex gap-2">
        <button
          v-for="p in visiblePollutants"
          :key="p.id"
          @click="togglePollutant(p.id)"
          class="px-4 py-2 text-xs rounded-xl transition-all duration-200 font-semibold shadow-md hover:shadow-lg transform hover:scale-105 ring-offset-2"
          :class="p.visible ? 'text-white ring-2 ring-white/70' : 'bg-gray-200 hover:bg-gray-300 text-gray-700 ring-0'"
          :style="p.visible ? { backgroundColor: p.color, boxShadow: `0 0 12px ${p.color}55` } : {}"
        >
          {{ p.label }}
        </button>
      </div>
    </div>
    
    <!-- 信息提示 -->
    <div v-if="selectedCity" class="flex-shrink-0 text-sm text-gray-700 mb-3 bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-xl border border-blue-200">
      <div class="flex items-center gap-2">
        <span class="text-lg">📍</span>
        <span class="font-semibold">{{ selectedCity.name }}</span> ({{ selectedCity.country }})
        <span v-if="comparedCity"> | <span class="font-semibold">{{ comparedCity.name }}</span> ({{ comparedCity.country }})</span>
      </div>
      <div class="mt-1 text-gray-600 text-xs flex flex-wrap items-center gap-x-3 gap-y-1">
        <span class="flex items-center gap-1"><span>💡</span> 右键其他城市加入对比</span>
        <span class="flex items-center gap-1 text-violet-700 font-medium"><span>✦</span> 在图表区移动鼠标可查看十字准线与就近月份读数</span>
      </div>
    </div>

    <div
      v-if="comparisonInsight"
      class="flex-shrink-0 text-sm mb-2 px-4 py-3 rounded-xl bg-gradient-to-r from-violet-50 via-fuchsia-50 to-indigo-50 border border-violet-200/80 text-slate-800 shadow-sm"
    >
      <span class="font-bold text-violet-800">探索洞察</span>
      <span class="ml-2 leading-relaxed">{{ comparisonInsight }}</span>
    </div>
    
    <div
      ref="chartRef"
      class="chart-plot-area flex-1 w-full min-h-[200px] basis-0 rounded-xl bg-gradient-to-b from-slate-50/90 to-white border border-slate-200/80 shadow-inner overflow-visible"
    ></div>
    
    <!-- WHO 指南说明 -->
    <div class="mt-4 flex-shrink-0 text-xs text-gray-600 border-t-2 border-purple-200 pt-3 bg-gradient-to-br from-purple-50 to-pink-50 p-3 rounded-xl">
      <div class="font-bold mb-2 flex items-center gap-2 text-gray-800">
        <span class="text-lg">🏥</span>
        <span>WHO 空气质量指南 (年均)</span>
      </div>
      <div class="grid grid-cols-2 gap-2">
        <div class="flex items-center gap-2 bg-white/50 p-2 rounded-lg">
          <span class="font-semibold">PM2.5:</span>
          <span class="text-gray-700">≤ 5 µg/m³</span>
        </div>
        <div class="flex items-center gap-2 bg-white/50 p-2 rounded-lg">
          <span class="font-semibold">PM10:</span>
          <span class="text-gray-700">≤ 15 µg/m³</span>
        </div>
        <div class="flex items-center gap-2 bg-white/50 p-2 rounded-lg">
          <span class="font-semibold">NO₂:</span>
          <span class="text-gray-700">≤ 10 µg/m³</span>
        </div>
        <div class="flex items-center gap-2 bg-white/50 p-2 rounded-lg">
          <span class="font-semibold">O₃:</span>
          <span class="text-gray-700">≤ 100 µg/m³</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed, nextTick } from 'vue'
import * as d3 from 'd3'
import { useData } from '../composables/useData'

const {
  selectedCityId,
  comparedCityId,
  selectedCityTimeSeries,
  comparedCityTimeSeries,
  getCityById
} = useData()

const chartRef = ref(null)
const visiblePollutants = ref([
  { id: 'pm25', label: 'PM2.5', visible: true, color: '#ef4444' },
  { id: 'pm10', label: 'PM10', visible: false, color: '#f97316' },
  { id: 'no2', label: 'NO₂', visible: false, color: '#3b82f6' },
  { id: 'o3', label: 'O₃', visible: false, color: '#10b981' }
])

const selectedCity = computed(() => getCityById(selectedCityId.value))
const comparedCity = computed(() => getCityById(comparedCityId.value))

/** 双城对比时的自动叙事，强化「洞见」与探索体验 */
const comparisonInsight = computed(() => {
  if (!comparedCity.value || !selectedCity.value) return ''
  const a = selectedCityTimeSeries.value
  const b = comparedCityTimeSeries.value
  if (!a.length || !b.length) return ''
  const ma = d3.mean(a, d => d.aqi)
  const mb = d3.mean(b, d => d.aqi)
  if (!Number.isFinite(ma) || !Number.isFinite(mb)) return ''
  const p = selectedCity.value.name
  const q = comparedCity.value.name
  if (Math.abs(ma - mb) < 4) {
    return `${p} 与 ${q} 在选定时段内平均 AQI 接近（约 ${ma.toFixed(0)} / ${mb.toFixed(0)}）。可打开多种污染物叠加以观察结构差异。`
  }
  const hi = ma >= mb ? p : q
  const lo = ma >= mb ? q : p
  const vmax = Math.max(ma, mb)
  const vmin = Math.min(ma, mb)
  const pct = vmin > 0 ? ((vmax - vmin) / vmin) * 100 : 100
  return `${hi} 的平均 AQI 较 ${lo} 高约 ${pct.toFixed(0)}%（${vmax.toFixed(1)} vs ${vmin.toFixed(1)}）。结合下方渐变面积与 WHO 虚线，可判断超标主要出现在哪些月份。`
})

// WHO 指南值
const whoGuidelines = {
  pm25: 5,
  pm10: 15,
  no2: 10,
  o3: 100
}

function togglePollutant(id) {
  const i = visiblePollutants.value.findIndex(v => v.id === id)
  if (i < 0) return
  visiblePollutants.value = visiblePollutants.value.map((v, idx) =>
    idx === i ? { ...v, visible: !v.visible } : v
  )
}

function nearestRow(rows, t) {
  if (!rows?.length) return null
  let best = rows[0]
  let bestD = Math.abs(+rows[0].date - +t)
  for (let i = 1; i < rows.length; i++) {
    const d = rows[i]
    const dt = Math.abs(+d.date - +t)
    if (dt < bestD) {
      bestD = dt
      best = d
    }
  }
  return best
}

function drawChart(arg) {
  const layoutRetry = typeof arg === 'number' && Number.isFinite(arg) ? arg : 0

  if (!chartRef.value) return

  if (!selectedCityTimeSeries.value.length) {
    d3.select(chartRef.value).selectAll('*').remove()
    d3.select(chartRef.value)
      .append('div')
      .attr('class', 'flex items-center justify-center h-full min-h-[160px] text-gray-400 text-sm px-2 text-center')
      .text('暂无数据，请选择一个城市')
    return
  }

  const data1 = selectedCityTimeSeries.value
  const data2 = comparedCityTimeSeries.value
  // 仅用 id + 数据判断：避免 getCityById 偶发未就绪时误判为无对比
  const hasCompare = data2.length > 0 && !!comparedCityId.value

  const margin = {
    top: 28,
    right: hasCompare ? 172 : 132,
    bottom: 74,
    left: 74
  }
  let width = Math.max(0, chartRef.value.clientWidth - margin.left - margin.right)
  let height = Math.max(0, chartRef.value.clientHeight - margin.top - margin.bottom)

  // flex 未算完高宽时多为 0：重试；仍不行则用保底尺寸画出 SVG，避免永久空白
  if (width < 40 || height < 40) {
    if (layoutRetry < 20) {
      requestAnimationFrame(() => drawChart(layoutRetry + 1))
      return
    }
    width = Math.max(width, 260)
    height = Math.max(height, 200)
  }

  d3.select(chartRef.value).selectAll('*').remove()

  const svgRoot = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .attr('overflow', 'visible')
    .style('overflow', 'visible')

  const svg = svgRoot.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  let activePollutants = visiblePollutants.value.filter(p => p.visible)
  if (activePollutants.length === 0) {
    activePollutants = [{ id: 'aqi', label: 'AQI', color: '#7c3aed' }]
  }
  const uid = 'u' + Math.random().toString(36).slice(2, 10)

  const allDates = [...data1.map(d => d.date), ...(hasCompare ? data2.map(d => d.date) : [])]
  const [t0, t1] = d3.extent(allDates)
  const x = d3.scaleTime()
    .domain(t0 && t1 ? [t0, t1] : d3.extent(data1, d => d.date))
    .range([0, width])

  const collectVals = (rows) =>
    rows.flatMap(d => activePollutants.map(p => d[p.id])).filter(v => v != null && Number.isFinite(v))
  const allValues = [...collectVals(data1), ...(hasCompare ? collectVals(data2) : [])]
  const yMaxRaw = allValues.length ? d3.max(allValues) : 100
  const yMax = Math.max(yMaxRaw * 1.12, 1)
  const y = d3.scaleLinear().domain([0, yMax]).range([height, 0]).nice()

  const yTicks = height > 0 ? Math.max(4, Math.min(10, Math.floor(height / 48))) : 6

  const defs = svgRoot.append('defs')
  const clipId = `plot-${uid}`
  defs.append('clipPath').attr('id', clipId)
    .append('rect')
    .attr('x', -2)
    .attr('y', -2)
    .attr('width', width + 4)
    .attr('height', height + 4)

  activePollutants.forEach(p => {
    ;[false, true].forEach(isSec => {
      const id = `grad-${uid}-${p.id}-${isSec ? 2 : 1}`
      const base = isSec ? d3.color(p.color).brighter(0.45) : d3.color(p.color)
      const g = defs.append('linearGradient').attr('id', id).attr('x1', '0%').attr('y1', '0%').attr('x2', '0%').attr('y2', '100%')
      g.append('stop').attr('offset', '0%').attr('stop-color', base).attr('stop-opacity', 0.35)
      g.append('stop').attr('offset', '100%').attr('stop-color', base).attr('stop-opacity', 0.02)
    })
  })

  const plot = svg.append('g').attr('clip-path', `url(#${clipId})`)

  const bgGrad = defs.append('radialGradient').attr('id', `chart-bg-${uid}`)
    .attr('cx', '50%').attr('cy', '0%').attr('r', '85%')
  bgGrad.append('stop').attr('offset', '0%').attr('stop-color', '#f8fafc')
  bgGrad.append('stop').attr('offset', '100%').attr('stop-color', '#eef2ff')

  plot.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', `url(#chart-bg-${uid})`)

  plot.append('g')
    .attr('class', 'grid-y')
    .call(d3.axisLeft(y).ticks(yTicks).tickSize(-width).tickFormat(''))
    .call(g => g.select('.domain').remove())
    .selectAll('.tick line')
    .attr('stroke', '#e2e8f0')
    .attr('stroke-dasharray', '2,3')

  activePollutants.forEach(pollutant => {
    const whoValue = whoGuidelines[pollutant.id]
    if (whoValue != null && whoValue <= y.domain()[1]) {
      plot.append('line')
        .attr('x1', 0)
        .attr('y1', y(whoValue))
        .attr('x2', width)
        .attr('y2', y(whoValue))
        .attr('stroke', pollutant.color)
        .attr('stroke-width', 1.2)
        .attr('stroke-dasharray', '6,4')
        .attr('opacity', 0.45)
    }
  })

  function drawSeries(data, city, isSecondary) {
    activePollutants.forEach(pollutant => {
      const strokeCol = isSecondary ? d3.color(pollutant.color).brighter(0.5) : pollutant.color
      const gid = `grad-${uid}-${pollutant.id}-${isSecondary ? 2 : 1}`

      const area = d3.area()
        .x(d => x(d.date))
        .y0(height)
        .y1(d => y(d[pollutant.id]))
        .defined(d => d[pollutant.id] != null && Number.isFinite(d[pollutant.id]))
        .curve(d3.curveMonotoneX)

      plot.append('path')
        .datum(data)
        .attr('fill', `url(#${gid})`)
        .attr('d', area)
        .attr('pointer-events', 'none')

      const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d[pollutant.id]))
        .defined(d => d[pollutant.id] != null && Number.isFinite(d[pollutant.id]))
        .curve(d3.curveMonotoneX)

      plot.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', strokeCol)
        .attr('stroke-width', isSecondary ? 1.8 : 2.6)
        .attr('stroke-linecap', 'round')
        .attr('stroke-linejoin', 'round')
        .attr('stroke-dasharray', isSecondary ? '6,4' : '')
        .attr('d', line)
        .attr('pointer-events', 'none')

      plot.selectAll(`.dot-${uid}-${pollutant.id}-${isSecondary ? 'b' : 'a'}`)
        .data(data.filter(d => d[pollutant.id] != null))
        .enter()
        .append('circle')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d[pollutant.id]))
        .attr('r', isSecondary ? 2.8 : 3.6)
        .attr('fill', strokeCol)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.2)
        .attr('opacity', 0.95)
        .append('title')
        .text(d => `${city.name} · ${pollutant.label}: ${d[pollutant.id].toFixed(1)} (${d3.timeFormat('%Y-%m')(d.date)})`)
    })
  }

  const cityMain = selectedCity.value || { name: '城市 A' }
  const cityCmp = comparedCity.value || { name: '对比城市' }
  drawSeries(data1, cityMain, false)
  if (hasCompare) drawSeries(data2, cityCmp, true)

  activePollutants.forEach(pollutant => {
    const whoValue = whoGuidelines[pollutant.id]
    if (whoValue != null && whoValue < y.domain()[1]) {
      svg.append('text')
        .attr('x', width - 4)
        .attr('y', y(whoValue) - 4)
        .attr('text-anchor', 'end')
        .attr('font-size', '9px')
        .attr('font-weight', '600')
        .attr('fill', pollutant.color)
        .text(`WHO ${whoValue}`)
    }
  })

  const xAxis = d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m'))
  if (width > 0) xAxis.ticks(Math.max(3, Math.min(12, Math.floor(width / 72))))

  const gx = svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(xAxis)
  gx.selectAll('text')
    .attr('transform', 'rotate(-38)')
    .style('text-anchor', 'end')
    .attr('dx', '-0.35em')
    .attr('dy', '0.42em')
    .attr('fill', '#64748b')
    .attr('font-size', '10px')
  gx.selectAll('.domain, .tick line').attr('stroke', '#cbd5e1')

  const gy = svg.append('g').call(d3.axisLeft(y).ticks(yTicks).tickFormat(d3.format('~s')))
  gy.selectAll('text').attr('fill', '#64748b').attr('font-size', '10px')
  gy.selectAll('.domain, .tick line').attr('stroke', '#cbd5e1')

  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + 54)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .attr('font-weight', '600')
    .attr('fill', '#475569')
    .text('时间')

  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -58)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .attr('font-weight', '600')
    .attr('fill', '#475569')
    .text('浓度 (µg/m³)')

  const focusLine = svg.append('line')
    .style('visibility', 'hidden')
    .attr('y1', 0)
    .attr('y2', height)
    .attr('stroke', '#6366f1')
    .attr('stroke-width', 1.25)
    .attr('stroke-dasharray', '4,3')
    .attr('pointer-events', 'none')
    .attr('opacity', 0.9)

  const tipG = svg.append('g').style('visibility', 'hidden').style('pointer-events', 'none')
  const tipBg = tipG.append('rect').attr('rx', 6).attr('fill', 'rgba(255,255,255,0.96)').attr('stroke', '#a5b4fc').attr('stroke-width', 1)
  const tipText = tipG.append('text').attr('font-size', '10px').attr('font-weight', '600').attr('fill', '#1e293b')

  svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'transparent')
    .style('cursor', 'crosshair')
    .on('mouseenter', () => {
      focusLine.style('visibility', 'visible')
      tipG.style('visibility', 'visible')
    })
    .on('mouseleave', () => {
      focusLine.style('visibility', 'hidden')
      tipG.style('visibility', 'hidden')
    })
    .on('mousemove', function (event) {
      const [mx] = d3.pointer(event, this)
      const [d0, d1] = x.domain()
      const t = x.invert(mx)
      if (+t < +d0 || +t > +d1) {
        focusLine.style('visibility', 'hidden')
        tipG.style('visibility', 'hidden')
        return
      }
      const r1 = nearestRow(data1, t)
      if (!r1) return
      const r2 = hasCompare ? nearestRow(data2, t) : null
      const xm = x(r1.date)
      focusLine.attr('x1', xm).attr('x2', xm).style('visibility', 'visible')
      tipG.style('visibility', 'visible')
      const parts = [d3.timeFormat('%Y-%m')(r1.date)]
      const short = (name) => (name && name.length > 2 ? name.slice(0, 2) : name || '')
      activePollutants.slice(0, 3).forEach(p => {
        const v1 = r1[p.id]
        const v2 = r2 && r2[p.id]
        let s = `${p.label} `
        if (v1 != null && Number.isFinite(v1)) s += `${short(selectedCity.value.name)}:${v1.toFixed(0)}`
        if (v2 != null && Number.isFinite(v2)) s += ` ${short(comparedCity.value?.name)}:${v2.toFixed(0)}`
        parts.push(s.trim())
      })
      const lineStr = parts.join('  ·  ')
      tipText.attr('x', 8).attr('y', 16).text(lineStr)
      const tw = Math.min(Math.max(120, lineStr.length * 5.5 + 20), width - 12)
      tipBg.attr('x', 2).attr('y', 2).attr('width', tw).attr('height', 24)
      let tx = xm + 12 > width * 0.52 ? xm - tw - 10 : xm + 12
      tx = Math.max(4, Math.min(tx, width - tw - 4))
      tipG.attr('transform', `translate(${tx}, 6)`)
    })

  const legend = svg.append('g').attr('transform', `translate(${width + 12}, 4)`)
  let legendY = 0
  legend.append('text')
    .attr('x', 0)
    .attr('y', legendY)
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .attr('fill', '#334155')
    .text(cityMain.name)
  legendY += 14
  activePollutants.forEach((p, i) => {
    const g = legend.append('g').attr('transform', `translate(0, ${legendY + i * 17})`)
    g.append('line')
      .attr('x1', 0).attr('y1', 9).attr('x2', 18).attr('y2', 9)
      .attr('stroke', p.color).attr('stroke-width', 2.5).attr('stroke-linecap', 'round')
    g.append('text')
      .attr('x', 22).attr('y', 12).attr('font-size', '10px').attr('fill', '#475569')
      .text(p.label)
  })
  legendY += activePollutants.length * 17 + 8
  if (hasCompare) {
    legend.append('text')
      .attr('x', 0)
      .attr('y', legendY)
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .attr('fill', '#334155')
      .text(cityCmp.name + ' (对比)')
    legendY += 14
    activePollutants.forEach((p, i) => {
      const g = legend.append('g').attr('transform', `translate(0, ${legendY + i * 17})`)
      g.append('line')
        .attr('x1', 0).attr('y1', 9).attr('x2', 18).attr('y2', 9)
        .attr('stroke', d3.color(p.color).brighter(0.5))
        .attr('stroke-width', 1.8)
        .attr('stroke-dasharray', '5,3')
      g.append('text')
        .attr('x', 22).attr('y', 12).attr('font-size', '10px').attr('fill', '#475569')
        .text(p.label)
    })
  }
}

watch(
  [selectedCityTimeSeries, comparedCityTimeSeries, visiblePollutants],
  () => drawChart(0),
  { deep: true, flush: 'post' }
)

let resizeObs
onMounted(() => {
  resizeObs = new ResizeObserver(() => drawChart(0))
  if (chartRef.value) resizeObs.observe(chartRef.value)
  nextTick(() => {
    requestAnimationFrame(() => drawChart(0))
  })
})

onUnmounted(() => {
  if (resizeObs) resizeObs.disconnect()
})
</script>
