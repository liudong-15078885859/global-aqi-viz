<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4 relative overflow-hidden">
    <!-- Animated background particles -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute w-2 h-2 bg-purple-400/20 rounded-full animate-float" style="top: 10%; left: 10%; animation-delay: 0s;"></div>
      <div class="absolute w-3 h-3 bg-blue-400/20 rounded-full animate-float" style="top: 20%; left: 80%; animation-delay: 1s;"></div>
      <div class="absolute w-2 h-2 bg-green-400/20 rounded-full animate-float" style="top: 60%; left: 30%; animation-delay: 2s;"></div>
      <div class="absolute w-4 h-4 bg-pink-400/20 rounded-full animate-float" style="top: 80%; left: 70%; animation-delay: 3s;"></div>
    </div>
    
    <header class="mb-6 relative z-10">
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl animate-fade-in text-center">
        <h1 class="text-4xl font-bold text-white mb-2 flex flex-wrap items-center justify-center gap-3">
          <span class="text-5xl animate-bounce-slow">🌍</span>
          <span class="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">全球空气质量指数 (AQI) 交互式探索</span>
        </h1>
        <p class="text-gray-200 text-lg max-w-4xl mx-auto leading-relaxed">
          数据来源: OpenAQ · 多视图联动：地图、时间刷选、折线十字准线、排行榜悬停与全景趋势线协同探索
        </p>
      </div>
    </header>
    
    <ControlPanel class="mb-6 relative z-10" ref="controlPanelRef" />
    
    <!-- lg 下固定视口高度：右侧「折线图 flex-1 + 排行榜固定高」之和必须 ≤ 行高，否则排行榜会向下溢出盖住页脚/设计说明 -->
    <div class="flex flex-col lg:flex-row gap-6 lg:h-[70vh] lg:min-h-0 relative z-10 lg:overflow-hidden">
      <div class="flex-1 min-h-[42vh] lg:min-h-0 bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
        <MapView ref="mapViewRef" />
      </div>
      <div class="w-full lg:w-2/5 flex flex-col gap-6 min-h-0 lg:h-full lg:shrink-0">
        <div class="flex-1 min-h-[280px] lg:min-h-0 overflow-hidden flex flex-col">
          <ChartView />
        </div>
        <div class="h-[40vh] max-h-[360px] shrink-0 min-h-0 overflow-hidden flex flex-col">
          <RankingView />
        </div>
      </div>
    </div>
    
    <!-- 说明文档链接 -->
    <footer class="mt-6 text-sm text-gray-200 text-center bg-white/10 backdrop-blur-lg p-4 rounded-2xl border border-white/20 shadow-xl relative z-20">
      <div class="mb-2">
        <a href="#documentation" class="underline text-blue-300 hover:text-blue-200 transition">查看设计说明文档</a> | 
        作业: 大数据可视化与可视分析 · 全球AQI交互探索
      </div>
      <div class="text-xs text-gray-300">
        基于 Vue 3 + D3.js 构建 | 部署于 GitHub Pages
      </div>
    </footer>

    <!-- 设计说明文档 -->
    <div id="documentation" class="mt-8 bg-white/10 backdrop-blur-lg p-8 rounded-2xl border border-white/20 shadow-2xl relative z-20">
      <h2 class="text-3xl font-bold mb-6 text-white">设计说明文档</h2>
      
      <section class="mb-6">
        <h3 class="text-2xl font-semibold mb-3 text-purple-300">1. 可视化方案旨在解答的问题</h3>
        <ul class="list-disc pl-6 space-y-2 text-gray-200">
          <li><strong>空间分布问题</strong>：全球不同地区的空气质量指数（AQI）存在怎样的空间分布差异？哪些区域污染最严重？</li>
          <li><strong>时间趋势问题</strong>：选定区域（国家或城市）的AQI及主要污染物浓度在时间上是如何变化的？是否存在季节性模式？</li>
          <li><strong>污染物结构问题</strong>：不同城市的污染"成分"有何不同？PM2.5、PM10、NO₂等污染物在各地AQI中扮演的角色如何？</li>
          <li><strong>跨视图协同问题（迭代）</strong>：在地图、时间刷选、趋势缩略图、折线与排名之间切换时，用户能否始终感知「当前时间窗」「当前城市」与「对比关系」，并快速得到可复述的结论（如双城差异幅度）？</li>
        </ul>
      </section>

      <section class="mb-6">
        <h3 class="text-2xl font-semibold mb-3 text-purple-300">2. 设计决策依据</h3>
        <div class="space-y-4 text-gray-200">
          <div>
            <strong class="text-white">可视化编码选择：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li>AQI值 → 颜色（色相/饱和度）：颜色是最直观表示等级的通道，用户可快速识别高污染区域</li>
              <li>城市地理位置 → 二维空间位置：地图投影天然适合展示地理分布模式</li>
              <li>AQI相对大小 → 气泡半径：辅助编码，增强城市间的视觉对比</li>
              <li>时间 → 水平轴位置：时间序列的标准编码，用户习惯</li>
              <li>污染物浓度 → 垂直轴位置 + 线条颜色：多曲线折线图清晰对比不同污染物的变化趋势</li>
              <li><strong>渐变面积（迭代）</strong>：在折线下方叠加沿污染物色相衰减的半透明面积，强化量级感知，并与 WHO 虚线参照形成「曲线—阈值—填充」三层可读结构</li>
              <li><strong>绘图区背景与网格（迭代）</strong>：径向渐变的浅底提升卡片层次感；水平虚线网格与坐标刻度对齐，便于逐月估读浓度</li>
              <li><strong>选中/对比/悬停编码（迭代）</strong>：地图上主选城市金色描边、对比城青色描边、跨视图悬停高亮白色外环，与排行榜条形同色逻辑一致，降低认知切换成本</li>
            </ul>
          </div>
          
          <div>
            <strong class="text-white">交互技术选择：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li><strong>缩放+平移</strong>：符合"概览→细节"的探索范式，用户可自由关注感兴趣的区域</li>
              <li><strong>刷选（Brushing）</strong>：比下拉选择更直观，支持连续范围选择，与NameVoyager的动态查询理念一致</li>
              <li><strong>按需显示细节（点击+折线图）</strong>：折线图能提供更丰富的时间趋势信息，符合"点击→深度探索"的交互模式</li>
              <li><strong>过滤器</strong>：简化视图、聚焦特定区域，避免信息过载</li>
              <li><strong>折线图十字准线与就近读数（迭代）</strong>：在绘图区移动鼠标时显示竖向参考线，并浮层展示当前刷选时段内、最接近指针时间的月份及所选污染物在主城/对比城的数值，属于细节层面的「焦点+上下文」辅助</li>
              <li><strong>排行榜与地图双向悬停联动（迭代）</strong>：共享全局 <code class="bg-white/10 px-1 rounded text-sm">hoveredCityId</code>，列表悬停即驱动地图气泡高亮，反之亦然，强化空间视图与排序视图的同一实体感</li>
              <li><strong>全景趋势线与时间窗叠层（迭代）</strong>：时间轴下方曲线改为「仅按国家过滤、不按当前刷选时间过滤」的全局平均 AQI 序列；紫带与两侧虚线标出当前 <code class="bg-white/10 px-1 rounded text-sm">timeRange</code>，与上方 brush 同源状态，体现经典 focus+context 结构</li>
            </ul>
          </div>

          <div>
            <strong class="text-white">多视图协调与状态设计（迭代）：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li>采用 <strong>Composable 模块级单例</strong>（<code class="bg-white/10 px-1 rounded text-sm">useData</code>）集中管理城市、测量、时间范围、选中/对比/悬停等城市 ID，避免多组件各自实例化导致的加载状态与数据不一致</li>
              <li><strong>时间</strong>由刷选、播放、全景趋势线共同读写同一 <code class="bg-white/10 px-1 rounded text-sm">timeRange</code>，地图聚合、折线序列、排名条形统计口径一致</li>
              <li><strong>选择</strong>由地图点击、排行榜点击、右键对比写入 <code class="bg-white/10 px-1 rounded text-sm">selectedCityId</code> / <code class="bg-white/10 px-1 rounded text-sm">comparedCityId</code>，折线图自动扩展双城时间并集与 Y 轴域，避免对比曲线落在坐标轴外</li>
              <li><strong>探索叙事</strong>：双城对比时根据两城平均 AQI 生成简短「探索洞察」文案，引导用户结合渐变面积与 WHO 线阅读超标月份，属于可视分析中的注释型引导（annotation-driven guidance）</li>
            </ul>
          </div>

          <div>
            <strong class="text-white">替代方案考量与选择依据：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li><strong>热力图 vs 气泡着色</strong>：考虑过热力图代替等值区域着色，但全球城市数据分布稀疏（仅25个城市），热力图会造成插值误导；气泡着色更能准确传达离散采样点的真实测量值</li>
              <li><strong>3D地球 vs 2D平面地图</strong>：考虑过3D地球仪展示，但交互复杂度高（需处理旋转、遮挡、投影变形），2D Mercator 平面地图对全球尺度的AQI对比已足够有效，且支持更直观的缩放平移</li>
              <li><strong>React vs Vue 3</strong>：考虑过React生态系统，但Vue 3的模板语法更直观简洁，Composition API 提供与 React Hooks 类似的逻辑复用能力，同时响应式系统自动追踪依赖，适合三周的开发周期</li>
              <li><strong>后端API vs 静态JSON</strong>：考虑过搭建后端服务动态查询OpenAQ API，但课程作业侧重前端可视化，且25城市×24个月的数据量仅约6000条记录，静态JSON可直接托管于GitHub Pages，降低部署复杂度</li>
              <li><strong>最终选择依据</strong>：综合考虑数据特征（稀疏离散点）、用户需求（快速对比+时间探索）、开发周期（3周）和部署便利性（静态托管），采用「2D地图气泡 + 时间刷选 + 多视图联动」的方案，在表达力与复杂度之间取得平衡</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="mb-6">
        <h3 class="text-2xl font-semibold mb-3 text-purple-300">3. 外部资源引用</h3>
        <div class="space-y-3 text-gray-200">
          <div>
            <strong class="text-white">数据源：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li><strong>OpenAQ 平台</strong>：世界最大的开源空气质量数据平台（https://openaq.org/），提供超过20亿条来自22,500+个地面监测站的实时与历史测量数据。本项目从中选取全球25个代表性城市的PM2.5、PM10、NO₂、O₃四项指标，聚合为2024年1月至2025年12月的月度统计数据</li>
              <li><strong>World Atlas (TopoJSON)</strong>：世界地图边界数据，来源于 Mike Bostock 维护的 TopoJSON 世界地图集（https://github.com/topojson/world-atlas），通过 jsDelivr CDN 加载 land-110m.json（1:110M 分辨率）。本地备份存放于 <code class="bg-white/10 px-1 rounded text-sm">public/data/world-110m.json</code></li>
            </ul>
          </div>
          <div>
            <strong class="text-white">技术与库引用：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li><strong>D3.js v7</strong>：数据驱动文档库，用于地图投影（d3-geo）、缩放平移（d3-zoom）、时间刷选（d3-brush）、坐标轴（d3-axis）、折线生成（d3-shape）等可视化核心功能（https://d3js.org/）</li>
              <li><strong>Vue 3 Composition API</strong>：前端框架，使用 <code class="bg-white/10 px-1 rounded text-sm">ref</code>、<code class="bg-white/10 px-1 rounded text-sm">computed</code>、<code class="bg-white/10 px-1 rounded text-sm">watch</code> 管理响应式状态与组件联动（https://vuejs.org/）</li>
              <li><strong>TopoJSON Client</strong>：将 TopoJSON 格式转换为 GeoJSON 以便 D3 渲染（https://github.com/topojson/topojson-client）</li>
              <li><strong>Tailwind CSS v3</strong>：原子化 CSS 框架，用于快速构建响应式布局与现代化 UI（https://tailwindcss.com/）</li>
              <li><strong>Vite</strong>：下一代前端构建工具，提供热模块替换（HMR）与快速开发体验（https://vitejs.dev/）</li>
            </ul>
          </div>
          <div>
            <strong class="text-white">设计规范与参考：</strong>
            <ul class="list-disc pl-6 mt-1">
              <li><strong>WHO 全球空气质量指南（2021版）</strong>：折线图中的 PM2.5（5 µg/m³）、PM10（15 µg/m³）、NO₂（10 µg/m³）、O₃（100 µg/m³）年均参考线来源（https://www.who.int/publications/i/item/9789240034228）</li>
              <li><strong>ColorBrewer 配色方案</strong>：AQI 等级颜色映射参考 Cynthia Brewer 的色彩设计原则，采用色相+饱和度双通道编码（https://colorbrewer2.org/）</li>
              <li><strong>美国 EPA AQI 标准</strong>：AQI 分级阈值（0-50 优、51-100 良、101-150 轻度污染等）参考美国环境保护署标准（https://www.airnow.gov/aqi/aqi-basics/）</li>
            </ul>
          </div>
          <div>
            <strong class="text-white">原创声明：</strong>
            <p class="mt-1">本项目为原创可视化作品，未改编或基于现有可视化案例。所有交互设计（如双城对比、十字准线、全景趋势线、悬停联动等）与视觉风格（玻璃态设计、深色主题、粒子动画等）均为自主设计与实现。</p>
          </div>
        </div>
      </section>

      <section class="mb-6">
        <h3 class="text-2xl font-semibold mb-3 text-purple-300">4. 开发流程概述</h3>
        <div class="text-gray-200">
          <p class="mb-3">
            开发本应用总工时约<strong class="text-purple-300">53小时</strong>（含后续迭代约3小时），分布在三周内完成。各阶段耗时分布如下：
          </p>
          <ul class="list-disc pl-6 space-y-2">
            <li><strong>数据准备（约7小时，13%）</strong>：从OpenAQ平台获取原始数据、数据清洗（处理缺失值与异常值）、聚合为月度统计（计算均值）、生成静态JSON文件（cities.json 与 measurements.json）。<em>关键难点</em>：确保25个城市在24个月内的数据完整性，处理部分城市某些月份数据缺失的情况。</li>
            <li><strong>地图核心功能（约10小时，19%）</strong>：D3地图绘制是技术难度最高的部分。包括：TopoJSON 转 GeoJSON、Mercator 投影配置、缩放平移行为（d3-zoom）调优、城市经纬度与地图像素坐标的对齐。<em>关键难点</em>：响应式布局下地图投影的自适应重算，以及城市气泡在不同缩放级别下的可见性。</li>
            <li><strong>交互联动（约12小时，23%）</strong>：时间轴刷选（d3-brush）与多视图联动是最耗时也是最重要的环节。需要设计好 Vue 响应式状态（timeRange、selectedCityId 等）的数据结构，确保各组件在状态变化时正确触发 D3 重绘。<em>关键难点</em>：刷选事件与 Vue watch 的同步，避免无限循环更新。</li>
            <li><strong>折线图与对比功能（约8小时，15%）</strong>：D3 折线图的绘制、坐标轴设置、多曲线显示（PM2.5/PM10/NO₂/O₃）、WHO 参考线以及多城市对比逻辑（右键添加对比城、双实线/虚线区分）。<em>关键难点</em>：双城时间并集与统一 Y 轴域的计算，避免对比曲线超出坐标轴范围。</li>
            <li><strong>界面美化与文档（约8小时，15%）</strong>：布局调优（Flexbox 响应式）、样式打磨（Tailwind CSS）、工具提示实现（自定义 Tooltip）、响应式适配（移动端堆叠布局）以及说明文档的撰写。<em>关键难点</em>：深色主题下的对比度与可读性平衡。</li>
            <li><strong>部署与测试（约5小时，9%）</strong>：GitHub Pages 配置、Vite base 路径调整、自动化部署流程（GitHub Actions）、跨浏览器测试（Chrome/Firefox/Safari）。<em>关键难点</em>：CDN 地图数据加载失败问题，改为本地备份 + CDN 降级策略。</li>
            <li><strong>Composable 单例与迭代（约3小时，6%）</strong>：将 <code class="bg-white/10 px-2 py-1 rounded text-sm">useData</code> 由「每次调用新建一份 ref」改为<strong>模块级单例状态</strong>，消除地图长期「加载中」、子视图数据不同步等问题；在此架构上补充 <code class="bg-white/10 px-2 py-1 rounded text-sm">hoveredCityId</code>、<code class="bg-white/10 px-2 py-1 rounded text-sm">globalTimeSparklineData</code> 等字段，完成排行榜–地图悬停联动、全景 Sparkline 时间窗叠层、折线图十字准线、渐变面积与对比洞察文案等增强，并联调与更新本节设计说明。</li>
          </ul>
          
          <div class="mt-5 p-4 bg-white/5 rounded-xl border border-white/10">
            <p class="mb-2">
              <strong class="text-white">哪些环节耗时最多？</strong>
            </p>
            <p class="text-sm leading-relaxed">
              <strong>交互联动（23%）</strong>与<strong>地图核心功能（19%）</strong>是耗时最多的两个环节。前者需要深入理解 Vue 响应式系统与 D3 数据驱动绘制的分工边界，后者涉及地理投影、拓扑数据转换等相对冷门的知识领域。建议后续项目早期花时间理清架构模式（如 Composable 单例），后续开发会更顺畅。
            </p>
          </div>

          <div class="mt-4 p-4 bg-white/5 rounded-xl border border-white/10">
            <p class="mb-2">
              <strong class="text-white">开发过程评述与经验总结：</strong>
            </p>
            <ul class="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Vue 与 D3 的分工</strong>：Vue 管理状态和布局，D3 负责数据驱动的视觉绘制，两者通过 <code class="bg-white/10 px-1 rounded text-sm">watch</code> 和 <code class="bg-white/10 px-1 rounded text-sm">computed</code> 建立桥梁。避免在 Vue 模板中直接操作 DOM，也避免在 D3 中管理应用状态。</li>
              <li><strong>响应式陷阱</strong>：早期遇到地图长期「加载中」的问题，根因是 <code class="bg-white/10 px-1 rounded text-sm">useData()</code> 在每个组件中调用时创建独立的 ref 实例，导致 <code class="bg-white/10 px-1 rounded text-sm">loading</code> 状态不同步。改为模块级单例后问题解决。</li>
              <li><strong>迭代开发策略</strong>：先实现核心功能（地图+刷选+折线），再逐步添加增强特性（对比、排行榜、十字准线、联动）。每次迭代后更新说明文档，避免最后补文档导致遗漏。</li>
              <li><strong>数据本地化</strong>：外部 CDN 资源（如世界地图 TopoJSON）应准备本地备份，避免网络波动导致应用不可用。</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="mb-6">
        <h3 class="text-2xl font-semibold mb-3 text-purple-300">5. 高级功能亮点</h3>
        <ul class="list-disc pl-6 space-y-2 text-gray-200">
          <li><strong>多城市对比</strong>：右键点击城市可加入对比；折线图取两城时间并集与统一 Y 域，主实线/对比虚线，并显示双行图例</li>
          <li><strong>对比洞察文案</strong>：自动比较两城平均 AQI（接近或差异百分比），提示结合面积与 WHO 虚线查看月份结构</li>
          <li><strong>时间轴播放</strong>：自动推进时间并动态更新地图，观察污染演变过程</li>
          <li><strong>全景 Sparkline + 当前时间窗</strong>：趋势线反映当前国家筛选下、全时间维度的平均 AQI；紫带与竖虚线标示当前刷选区间，与主刷选条联动</li>
          <li><strong>折线图十字准线</strong>：鼠标移动显示竖线及浮动读数（月份 + 各可见污染物双城数值）</li>
          <li><strong>地图 ⟷ 排行榜悬停联动</strong>：悬停一方即可在另一方高亮同一城市，选中/对比态另有金/青编码</li>
          <li><strong>WHO 指南参考线</strong>：折线图上以虚线标示各污染物指导值，绘图区内弱化、轴旁保留标签</li>
          <li><strong>智能标签显示</strong>：仅为污染较严重的城市显示名称标签，避免视觉混乱</li>
          <li><strong>动画与视觉层次</strong>：城市气泡展开、排名条形宽度过渡、折线平滑与渐变面积、污染物切换按钮发光强调；页头标题居中排版以增强陈述感</li>
        </ul>
      </section>

      <section>
        <h3 class="text-2xl font-semibold mb-3 text-purple-300">6. 迭代小结</h3>
        <div class="space-y-3 text-gray-200 text-sm leading-relaxed">
          <p>
            <strong class="text-white">高级交互：</strong>十字准线就近读数、刷选与全景趋势 focus+context、播放、缩放平移、右键对比、污染物多选切换。
          </p>
          <p>
            <strong class="text-white">创新可视化元素：</strong>渐变面积、径向绘图区背景、污染严重城市的粒子示意、排名与地图的同步高亮环。
          </p>
          <p>
            <strong class="text-white">有效的多视图协调：</strong>单一数据源状态驱动地图、控制条、折线图、排行榜；时间窗与选择在各视图中语义一致。
          </p>
          <p>
            <strong class="text-white">图形设计：</strong>统一的 slate / 紫系界面层次、图例与轴标签对比度、对比模式下加宽边距与裁剪区避免元素溢出。
          </p>
          <p>
            <strong class="text-white">探索体验：</strong>洞察文案降低对比场景的解读门槛；操作提示散布在页头、控制条与图表旁，支持从概览到细节的持续探索。
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ControlPanel from './components/ControlPanel.vue'
import MapView from './components/MapView.vue'
import ChartView from './components/ChartView.vue'
import RankingView from './components/RankingView.vue'
import { useData } from './composables/useData'

const { loadData, stopPlay } = useData()
const mapViewRef = ref(null)
const controlPanelRef = ref(null)

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  stopPlay()
})
</script>

<style scoped>
/* 平滑滚动 */
html {
  scroll-behavior: smooth;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: rgba(168, 85, 247, 0.6);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(168, 85, 247, 0.8);
}

/* 浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-20px) translateX(10px);
  }
  50% {
    transform: translateY(-10px) translateX(-10px);
  }
  75% {
    transform: translateY(-30px) translateX(5px);
  }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

/* 慢速弹跳动画 */
@keyframes bounceSlow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce-slow {
  animation: bounceSlow 3s ease-in-out infinite;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s ease-in-out infinite;
}
</style>
