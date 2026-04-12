# 🚀 GitHub Pages 部署完整指南

## 📋 部署前准备

### 1. 确认项目配置

您的项目已经配置好以下关键文件：

#### ✅ `vite.config.js`
```javascript
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  base: './',  // ✓ 使用相对路径，适配 GitHub Pages
})
```

#### ✅ `.github/workflows/deploy.yml`
已配置自动化部署工作流，推送到 `main` 分支时自动构建并部署。

---

## 🎯 部署步骤（两种方法）

### 方法一：自动化部署（推荐）⭐

#### Step 1: 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 **"+"** → **"New repository"**
3. 填写仓库信息：
   - **Repository name**: `global-aqi-viz`（或您喜欢的名称）
   - **Description**: 全球空气质量指数交互式可视化
   - **Visibility**: Public（GitHub Pages 免费仅支持公开仓库）
   - **不要勾选** "Initialize this repository with a README"
4. 点击 **"Create repository"**

#### Step 2: 推送代码到 GitHub

在您的项目根目录执行：

```bash
# 进入项目目录
cd c:\Users\ld200\Desktop\可视化交互9\global-aqi-viz

# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Global AQI Visualization"

# 添加远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/global-aqi-viz.git

# 推送到 main 分支
git branch -M main
git push -u origin main
```

> ⚠️ **注意**: 将 `YOUR_USERNAME` 替换为您的 GitHub 用户名

#### Step 3: 启用 GitHub Pages

1. 在 GitHub 仓库页面，点击 **"Settings"**（设置）
2. 左侧菜单找到 **"Pages"**
3. 在 **"Build and deployment"** 部分：
   - **Source**: 选择 **"Deploy from a branch"**
   - **Branch**: 选择 **`gh-pages`** 分支
   - **Folder**: 选择 **`/ (root)`**
4. 点击 **"Save"**

#### Step 4: 等待自动部署

1. 推送代码后，GitHub Actions 会自动运行
2. 点击仓库顶部的 **"Actions"** 标签查看部署进度
3. 通常需要 1-3 分钟完成构建和部署
4. 成功后，`gh-pages` 分支会自动创建

#### Step 5: 访问您的网站

部署成功后，您的网站将在以下地址可用：

```
https://YOUR_USERNAME.github.io/global-aqi-viz/
```

---

### 方法二：手动部署

如果自动化部署遇到问题，可以手动部署：

#### Step 1: 本地构建项目

```bash
# 确保所有依赖已安装
npm install

# 构建生产版本
npm run build
```

构建完成后，会在 `dist/` 目录生成静态文件。

#### Step 2: 部署到 gh-pages 分支

```bash
# 安装 gh-pages 工具（首次需要）
npm install -D gh-pages

# 部署 dist 目录到 gh-pages 分支
npx gh-pages -d dist
```

#### Step 3: 在 GitHub 启用 Pages

同方法一的 Step 3。

---

## 🔧 常见问题与解决方案

### ❌ 问题 1: 页面显示空白或 404

**原因**: `base` 路径配置不正确

**解决方案**:
```javascript
// vite.config.js
export default defineConfig({
  // 如果仓库名是 global-aqi-viz
  base: '/global-aqi-viz/',  // 使用仓库名作为路径
  
  // 或者使用相对路径（推荐，更灵活）
  base: './',
})
```

修改后重新构建并推送：
```bash
git add vite.config.js
git commit -m "Fix base path for GitHub Pages"
git push
```

### ❌ 问题 2: 地图数据加载失败

**原因**: CDN 资源被阻塞或网络问题

**解决方案**: ✅ 已解决！项目已将世界地图数据本地化到 `public/data/world-110m.json`

### ❌ 问题 3: GitHub Actions 构建失败

**常见错误**: Node.js 版本不兼容

**解决方案**: 检查 `.github/workflows/deploy.yml` 中的 Node 版本：
```yaml
- name: Setup Node
  uses: actions/setup-node@v3
  with:
    node-version: 18  # 确保使用 Node 18 或更高版本
    cache: 'npm'
```

### ❌ 问题 4: 样式丢失或图片不显示

**原因**: 资源路径问题

**解决方案**:
1. 确保 `vite.config.js` 中 `base: './'` 或 `base: '/仓库名/'`
2. 所有静态文件放在 `public/` 目录
3. 代码中使用相对路径引用资源

---

## 📊 部署后检查清单

访问您的 GitHub Pages 网站后，请检查：

- [ ] 页面正常加载，无空白
- [ ] 地图数据正常显示（世界地图 + 城市气泡）
- [ ] 时间轴刷选可以交互
- [ ] 点击城市显示折线图
- [ ] 国家选择器工作正常
- [ ] 排行榜正常显示
- [ ] 所有样式正常（深色主题、渐变色等）
- [ ] 浏览器控制台无错误（F12 检查）

---

## 🔄 更新部署

每次修改代码后，只需：

```bash
# 提交更改
git add .
git commit -m "描述您的更新"

# 推送到 main 分支
git push

# GitHub Actions 会自动构建并部署！
```

---

## 🌐 自定义域名（可选）

如果您想使用自己的域名：

### Step 1: 创建 CNAME 文件

在项目 `public/` 目录创建 `CNAME` 文件：
```
your-domain.com
```

### Step 2: 配置 DNS

在您的域名注册商处添加 CNAME 记录：
```
类型: CNAME
名称: www
值: YOUR_USERNAME.github.io
```

### Step 3: 在 GitHub 配置域名

1. 仓库 **Settings** → **Pages**
2. 在 **Custom domain** 输入您的域名
3. 点击 **"Save"**
4. 勾选 **"Enforce HTTPS"**

---

## 📈 性能优化建议

### 1. 启用压缩

GitHub Pages 自动启用 gzip 压缩，无需额外配置。

### 2. 优化构建大小

查看构建大小：
```bash
npm run build
```

当前项目构建后约：
- JavaScript: ~300KB (压缩后 ~100KB)
- CSS: ~50KB (压缩后 ~15KB)
- 数据文件: ~110KB

### 3. 使用 CDN 加速

GitHub Pages 自带 Cloudflare CDN，全球访问速度较快。

---

## 🎓 作业提交说明

部署完成后，提交以下内容：

1. **GitHub 仓库链接**: `https://github.com/YOUR_USERNAME/global-aqi-viz`
2. **在线演示链接**: `https://YOUR_USERNAME.github.io/global-aqi-viz/`
3. **说明文档**: 已包含在页面底部的设计说明文档中

### 作业要求对照：
✅ 可视化作品托管于 GitHub Pages  
✅ 说明文档与可视化作品置于同一页面（页面底部）  
✅ 包含所有必需内容：
  - 可视化方案旨在解答的问题
  - 设计决策依据与替代方案
  - 外部资源引用
  - 开发流程概述与工时统计

---

## 🆘 获取帮助

如果遇到问题：

1. **查看 Actions 日志**: 仓库 → Actions → 点击失败的工作流 → 查看日志
2. **检查浏览器控制台**: F12 → Console 查看错误信息
3. **验证构建**: 本地运行 `npm run build` 确保无错误
4. **检查网络请求**: F12 → Network 查看哪些资源加载失败

---

## ✨ 部署成功标志

当您看到以下内容时，说明部署成功：

```
✅ GitHub Actions 显示绿色对勾
✅ gh-pages 分支已创建
✅ 访问 https://YOUR_USERNAME.github.io/global-aqi-viz/ 正常显示
✅ 所有交互功能正常工作
✅ 页面底部设计说明文档完整显示
```

---

## 📝 快速部署命令总结

```bash
# 1. 首次部署
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/global-aqi-viz.git
git branch -M main
git push -u origin main

# 2. 后续更新
git add .
git commit -m "Update description"
git push

# 3. 手动部署（可选）
npm run build
npx gh-pages -d dist
```

---

**祝您部署顺利！** 🎉

如有问题，请查看 GitHub Actions 日志或浏览器控制台错误信息。
