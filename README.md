# Markdown Opener

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Tauri](https://img.shields.io/badge/Tauri-2.0-FFC131?style=for-the-badge&logo=tauri&logoColor=white)
![marked](https://img.shields.io/badge/marked-000000?style=for-the-badge&logo=markdown&logoColor=white)
![highlight.js](https://img.shields.io/badge/highlight.js-393C3E?style=for-the-badge&logo=highlight.js&logoColor=white)
![KaTeX](https://img.shields.io/badge/KaTeX-008080?style=for-the-badge&logo=katex&logoColor=white)
![Mermaid](https://img.shields.io/badge/Mermaid-FF3670?style=for-the-badge&logo=mermaid&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

---

![MIT License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=flat-square)
![Made with Love](https://img.shields.io/badge/Made%20with-❤️-ff69b4?style=flat-square)

一个基于 Tauri 的轻量级 Markdown 查看器和编辑器，支持 Windows、macOS 和 Linux。

## ✨ 特性

- 📝 **实时预览** - 支持实时编辑和预览 Markdown
- 🎨 **主题切换** - 支持浅色和深色主题
- 📂 **文件浏览器** - 内置文件浏览器，快速浏览文件夹
- 🎯 **布局模式** - 支持编辑、预览、拆分三种布局模式
- 📐 **代码高亮** - 支持多种编程语言的代码高亮
- 🔢 **数学公式** - 支持 LaTeX 数学公式渲染
- 📊 **图表支持** - 支持 Mermaid 图表
- 💾 **文件操作** - 支持打开、保存 Markdown 文件
- 🖱️ **拖放支持** - 支持拖放文件打开

## 🚀 技术栈

| 技术 | 说明 | 徽章 |
|------|------|------|
| **前端语言** | TypeScript + JavaScript | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) ![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **桌面框架** | Tauri 2.0 | ![Tauri](https://img.shields.io/badge/Tauri-2.0-FFC131?style=flat-square&logo=tauri&logoColor=white) |
| **Markdown 解析** | marked | ![marked](https://img.shields.io/badge/marked-000000?style=flat-square&logo=markdown&logoColor=white) |
| **代码高亮** | highlight.js | ![highlight.js](https://img.shields.io/badge/highlight.js-393C3E?style=flat-square&logo=highlight.js&logoColor=white) |
| **数学公式** | KaTeX | ![KaTeX](https://img.shields.io/badge/KaTeX-008080?style=flat-square&logo=katex&logoColor=white) |
| **图表渲染** | Mermaid | ![Mermaid](https://img.shields.io/badge/Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white) |
| **构建工具** | Vite | ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white) |

## 📦 下载和使用

### 方式一：直接使用（推荐）

无需安装任何依赖，直接下载对应平台的可执行文件运行即可！

| 平台 | 下载地址 |
|------|----------|
| Windows | [app.exe](https://github.com/starking-zl/markdown-opener/releases) |
| macOS | [markdown-opener.app](https://github.com/starking-zl/markdown-opener/releases) |
| Linux | [markdown-opener](https://github.com/starking-zl/markdown-opener/releases) |

### 方式二：从源码构建（开发者）

如果你想自己构建应用：

```bash
# 前置要求
- Node.js 18+
- Rust 1.77+
- pnpm (推荐) 或 npm

# 安装依赖
pnpm install

# 运行开发服务器
pnpm tauri dev

# 构建生产版本
pnpm tauri build

# 构建产物位置
- Windows: `src-tauri/target/release/app.exe`
- macOS: `src-tauri/target/release/markdown-opener.app`
- Linux: `src-tauri/target/release/markdown-opener`
```

## 🎮 使用说明

1. **打开文件**: 点击顶部工具栏的"打开文件"按钮
2. **文件浏览器**: 点击"刷新"按钮选择文件夹浏览
3. **布局切换**: 使用顶部中央的三个按钮切换视图模式
4. **侧边栏**: 点击右上角的菜单图标可以折叠/展开侧边栏
5. **主题切换**: 点击右上角的太阳/月亮图标切换主题
6. **保存文件**: 点击工具栏的"保存"按钮保存修改

## 📝 支持的 Markdown 特性

- 标题、段落、换行
- 粗体、斜体、删除线
- 链接和图片
- 代码块和行内代码
- 列表（有序、无序）
- 引用块
- 表格
- 水平线
- 数学公式（行内 `$...$` 和块级 `$$...$$`）
- Mermaid 图表

## 🌟 预览

### 浅色主题
![Light Theme](https://raw.githubusercontent.com/starking-zl/markdown-opener/main/assets/screenshots/light-theme.png)

### 深色主题
![Dark Theme](https://raw.githubusercontent.com/starking-zl/markdown-opener/main/assets/screenshots/dark-theme.png)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🛠️ 开发指南

### 项目结构

```
.
├── src/                  # 前端源代码
│   ├── main.ts          # 主逻辑
│   └── style.css       # 样式文件
├── src-tauri/           # Tauri 后端代码
│   ├── src/             # Rust 源代码
│   ├── Cargo.toml       # Rust 依赖配置
│   └── tauri.conf.json  # Tauri 配置文件
├── package.json         # Node.js 依赖配置
└── vite.config.ts       # Vite 配置文件
```

### 添加新功能

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📧 联系方式

- 项目主页: https://github.com/starking-zl/markdown-opener
- 问题反馈: https://github.com/starking-zl/markdown-opener/issues

## 🙏 致谢

- [Tauri](https://tauri.app/) - 构建跨平台桌面应用
- [marked](https://marked.js.org/) - Markdown 解析
- [highlight.js](https://highlightjs.org/) - 代码高亮
- [KaTeX](https://katex.org/) - 数学公式渲染
- [Mermaid](https://mermaid.js.org/) - 图表渲染

---

Made with ❤️ using Tauri
