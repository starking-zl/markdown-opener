# Markdown Opener 使用指南

## 当前状态

### ✅ 前端已就绪
- Vite 开发服务器运行中
- 预览地址: http://localhost:5173/

### ⚠️ 桌面功能需要初始化
由于浏览器安全限制，文件读取功能需要完整的 Tauri 桌面应用环境。

---

## 如何运行

### 方案一：浏览器预览（快速测试）
访问 http://localhost:5173/

**功能限制**：无法读取本地文件，只能在编辑器中手动输入内容

---

### 方案二：完整桌面应用（推荐）

#### 1. 初始化 Tauri 项目

在终端中运行：
```bash
npx tauri init
```

提示信息时请按以下方式回答：
```
? App name: Markdown Opener
? Window title: Markdown Opener  
? Frontend dist: ../dist
? Dev URL: http://localhost:5173
? Before dev command: npm run vite:dev
? Before build command: npm run build
```

#### 2. 启动开发模式
```bash
npm run tauri dev
```

#### 3. 构建发布版本
```bash
npm run tauri build
```

---

## 功能特性

- 📝 Markdown 实时预览
- 🎨 语法高亮
- 📐 数学公式支持
- 📊 图表支持
- 🌙 深色/浅色主题
- 📁 文件浏览器
- 💾 文件保存/导出
- 📤 HTML 导出

---

## 技术栈

- Tauri 2.0
- TypeScript
- Vite
- Marked
- Highlight.js
- KaTeX
- Mermaid

---

## 注意事项

1. **首次运行需要网络** - 需要下载 Rust 工具链和依赖
2. **Windows 用户** - 需要安装 Visual Studio Build Tools
3. **macOS 用户** - 需要安装 Xcode Command Line Tools
4. **Linux 用户** - 需要安装 WebKit2GTK 开发库

---

## 快速问题排查

**Q: 无法打开文件？**  
A: 请确保使用 `npm run tauri dev` 运行完整桌面应用，而非仅在浏览器中打开。

**Q: 构建失败？**  
A: 检查 Rust 和 Node.js 是否正确安装：
```bash
rustc --version
node --version
```

**Q: 下载依赖很慢？**  
A: 可以配置 Rust 镜像源，参考 https://rsproxy.cn/
