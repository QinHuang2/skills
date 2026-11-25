# Agent Skills Collection (`QinHuang2/skills`)

一套面向 **Antigravity / Claude Code / Codex / Cursor** 的高审美视觉设计、技术机械图解与代码驱动视频制作 Skills 集合。每个 Skill 均遵循标准 `SKILL.md` 渐进式披露规范，内置参考规范库（`references/`）与零额外依赖可执行的 Python 辅助工具链（`scripts/`）。

---

## 目录速览

| Skill 目录 | 核心定位 | 对标/演进设计参考 | 主要产物 |
| :--- | :--- | :--- | :--- |
| [`logo-create-skill`](./logo-create-skill) | 纯文字输入生成高定透明底艺术字/标题 Logo | Typography-First Spec | `1360x560` 透明通道 PNG |
| [`html-design-studio`](./html-design-studio) | HTML 原生视觉设计工作室（三方向提案 + 品牌锁 + PPTX 导出） | `huashu-design` | 交互网页原型、社媒海报、可编辑 `.pptx` |
| [`motion-launch-director`](./motion-launch-director) | 确定性代码驱动商业宣传片与动态图形导演 | `huashu-motion` | 交互审片舞台、程序化 `.wav` 配乐、`.mp4` + 质检表 |
| [`isometric-anatomy`](./isometric-anatomy) | 抽象算法与架构的「可交互等距机械装置」解剖图解 | `anatomy` | 四阶阴影等距 `.svg` / 实时数学联动 `.html` |
| [`srt-whiteboard-animator`](./srt-whiteboard-animator) | SRT 字幕驱动的暖米色纸张流式手绘白板讲解动画 | `srt-whiteboard-animation` | 分镜标注预览台、`ink -> color` 手绘 `.mp4` |
| [`vertical-shorts-editor`](./vertical-shorts-editor) | 9:16 竖屏口播短视频蓝图精剪、安全区校验与动效包装 | `vertical-motion-editor` | `1080x1920` `.mp4`、卡拉 OK `.ass`、Remotion 工程 |

---

## 各 Skill 核心能力说明

### 1. `html-design-studio`
- **三方向并行提案**：拒绝千篇一律的 AI 紫蓝渐变模板，基于 12 种视觉母体先输出 3 套差异化视觉方向草案供确认。
- **五步品牌资产锁定**：通过 `brand-lock.json` 锁定色彩 Token 与字体栈，`scripts/design_lint.py` 自动校验 WCAG 对比度与反套路规范。
- **原生 PPTX 导出**：`scripts/html_slides_to_pptx.py` 可将 `<section data-slide>` 结构化演示文稿一键编译为 PowerPoint / Keynote 可直接编辑的 `.pptx` 文件。

### 2. `motion-launch-director`
- **确定性时间轴契约**：所有画面状态均为 `window.__seek(t)` 的纯函数，零随机抖动，支持任意帧精确跳转。
- **指帧批注审片台（Point-at-the-Frame）**：内置 Studio HUD，点击画面任意位置即可复制带时间戳、场景 ID、坐标百分比与选择器定位的修订 JSON。
- **程序化音效与渲染质检**：`scripts/motion_cli.py` 支持一键脚手架（`new`）、静态契约检查（`check`）、从 `cues.json` 合成双声道音效（`sound`），以及 FFmpeg 死帧检测与抽帧缩略图质检表生成（`qa --sheet`）。

### 3. `isometric-anatomy`
- **数学逻辑先行**：先建立系统的真实状态方程，再映射为黄铜管路、玻璃视液管、擒纵齿轮、压力表盘等物理机械隐喻。
- **标准 30° 等距投影引擎**：`scripts/iso_kit.py` 按画家算法（Painter's Order）自动深度排序并生成四阶受光阴影 SVG 或带滑块实时联动的独立 HTML。
- **几何与标注审计**：`scripts/audit_figure.py` 自动排查退化多边形、越界顶点与文字标签重叠。

### 4. `srt-whiteboard-animator`
- **字幕驱动流式作画**：`scripts/parse_srt.py` 将 `.srt` 智能切分为 25–35 秒叙事场景；画面随旁白推进按 **墨迹勾线（`ink`）→ 彩笔上色（`color`）** 两阶段流式呈现。
- **防覆盖保护与交互预览**：`scripts/render_whiteboard.py preview` 生成本地 `preview.html` 控制台并检测受保护分区重叠，确认后再流式渲染与多场景无损合并（`render` / `merge`）。

### 5. `vertical-shorts-editor`
- **代码化剪辑蓝图（`plan.json`）**：统一编排前 3 秒黄金 Hook 横幅、按语气的推镜裁切（Punch-in cuts）、逐词高亮动态字幕、B-roll 空镜与数据卡片。
- **9:16 平台安全区硬校验**：`scripts/validate_plan.py` 自动拦截侵入顶部状态栏、右侧互动按钮栏、底部进度条或遮挡人物面部的元素。
- **双引擎编译**：`scripts/compile_vertical.py`既可直接调用 FFmpeg 输出 `1080x1920` 成片与 `.ass` 动态字幕（在无 `libass` 环境下自动回退 macOS CoreText 高清图层合成），也可一键生成完整 Remotion TypeScript 工程（`scaffold-remotion`）。

---

## 安装方式

### Antigravity 全局安装
将各 Skill 目录复制到 `~/.gemini/config/skills/` 下即可全局按需激活：

```bash
git clone https://github.com/QinHuang2/skills.git
mkdir -p ~/.gemini/config/skills
cp -R skills/*-studio skills/*-director skills/isometric-anatomy skills/srt-whiteboard-animator skills/vertical-shorts-editor skills/logo-create-skill ~/.gemini/config/skills/
```

### Claude Code / Codex / Skills CLI
```bash
npx skills add QinHuang2/skills
```
