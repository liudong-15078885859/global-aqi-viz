# 全球AQI可视化 - 部署指南

## 本地开发

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```
访问: http://localhost:5173/global-aqi-viz/

### 3. 构建生产版本
```bash
npm run build
```

### 4. 预览生产构建
```bash
npm run preview
```

---

## GitHub Pages 部署

### 方法一：GitHub Actions 自动部署（推荐）

#### 步骤1: 创建GitHub仓库
```bash
git init
git add .
git commit -m "Initial commit: Global AQI Visualization"
```

#### 步骤2: 推送到GitHub
```bash
git remote add origin https://github.com/[YOUR_USERNAME]/global-aqi-viz.git
git branch -M main
git push -u origin main
```

#### 步骤3: 自动部署
- GitHub Actions会自动触发构建（见`.github/workflows/deploy.yml`）
- 等待2-3分钟，构建产物会自动部署到`gh-pages`分支

#### 步骤4: 启用GitHub Pages
1. 进入仓库 **Settings** → **Pages**
2. 在 **Source** 下拉框中选择 **gh-pages** 分支
3. 点击 **Save**
4. 等待1-2分钟，访问: `https://[YOUR_USERNAME].github.io/global-aqi-viz/`

---

### 方法二：手动部署

#### 步骤1: 构建项目
```bash
npm run build
```

#### 步骤2: 创建gh-pages分支
```bash
cd dist
git init
git add .
git commit -m "Deploy to GitHub Pages"
git branch -M gh-pages
git remote add origin https://github.com/[YOUR_USERNAME]/global-aqi-viz.git
git push -f origin gh-pages
```

#### 步骤3: 启用GitHub Pages
同上，在Settings中启用gh-pages分支。

---

## 常见问题

### Q1: 页面显示空白
**原因**: `vite.config.js`中的`base`路径与仓库名不匹配

**解决**: 修改`vite.config.js`:
```javascript
export default defineConfig({
  base: '/global-aqi-viz/',  // 必须与仓库名一致
  // ...
})
```

### Q2: 数据文件加载失败
**原因**: 数据文件路径错误

**解决**: 确保数据文件在`public/data/`目录下，使用绝对路径访问:
```javascript
fetch('/data/cities.json')  // 正确
fetch('./data/cities.json') // 错误
```

### Q3: GitHub Actions构建失败
**原因**: Node版本不兼容

**解决**: 检查`.github/workflows/deploy.yml`中的Node版本:
```yaml
- name: Setup Node
  uses: actions/setup-node@v3
  with:
    node-version: 18  # 使用18或更高版本
```

### Q4: 地图不显示
**原因**: TopoJSON库未加载

**解决**: 确保`index.html`中包含:
```html
<script src="https://cdn.jsdelivr.net/npm/topojson@3.0.2/dist/topojson.min.js"></script>
```

---

## 项目检查清单

部署前请确认：

- [ ] 所有依赖已安装（`npm install`）
- [ ] 本地开发服务器正常运行（`npm run dev`）
- [ ] 构建无错误（`npm run build`）
- [ ] `vite.config.js`中的`base`路径正确
- [ ] 数据文件在`public/data/`目录下
- [ ] `.nojekyll`文件存在（防止GitHub Pages使用Jekyll）
- [ ] `.github/workflows/deploy.yml`配置正确
- [ ] README.md和report.md已更新

---

## 访问地址

部署成功后，可通过以下地址访问：

- **主页**: https://[YOUR_USERNAME].github.io/global-aqi-viz/
- **仓库**: https://github.com/[YOUR_USERNAME]/global-aqi-viz

---

## 更新部署

每次推送到`main`分支时，GitHub Actions会自动触发新的部署：

```bash
git add .
git commit -m "Update: [描述更改]"
git push origin main
```

等待2-3分钟后，刷新页面即可看到更新。

---

## 技术支持

如有问题，请参考：
- 项目README: README.md
- 设计报告: report.md
- D3.js文档: https://d3js.org/
- Vue 3文档: https://vuejs.org/
