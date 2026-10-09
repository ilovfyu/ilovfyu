# 怎么把这份主页发布出去 · Setup

给 `ilovfyu` 的 GitHub 主页设计。主题是**「你的名字」黄昏天空（kataware-doki）**，中英双语，亮/暗自动切换。

---

## 1. 发布（已经完成了）

GitHub 有个约定：**只要存在一个和用户名同名的仓库，它的 README 就会显示在你的主页顶部。**
仓库 `ilovfyu/ilovfyu` 已经存在，内容也已经推上去了 —— 打开 <https://github.com/ilovfyu> 就能看到。

远端默认分支是 **`master`**（不是 `main`，建仓时定的）。当前配置：

```
origin  git@github.com:ilovfyu/ilovfyu.git   （SSH，密钥 ~/.ssh/id_ed25519）
分支    master
```

### 以后改完怎么推

```bash
git add -A
git commit -m "描述你改了什么"
git push
```

### 万一要重来一遍（在新机器上）

```bash
git clone git@github.com:ilovfyu/ilovfyu.git
cd ilovfyu
python3 tools/build_assets.py      # 离线重绘装饰素材
python3 tools/build_heatmap.py     # 联网拉最新贡献数据并重绘
```

> 仓库必须是 **public**，否则主页不显示（当前已是 public）。

### 推完第一件事：手动跑一次 Action

`.github/workflows/refresh-contributions.yml` 只在**定时**和**手动**时触发，所以刚推完不会自己跑。
去 <https://github.com/ilovfyu/ilovfyu/actions> → 选中 **Refresh contribution cards** → 点
**Run workflow**，确认它能把贡献卡片刷新并提交回来。

如果这一步报 **403 / permission denied**：

> 仓库 **Settings → Actions → General → Workflow permissions**，
> 选 **Read and write permissions** 然后保存。
> 新版仓库默认可能是只读，那样 Action 就推不回来。

---

## 2. 本地预览

不想每次都推上去才知道好不好看，直接开预览页：

```bash
open preview.html          # 亮色
open 'preview.html#dark'   # 暗色（或者点右上角按钮切换）
```

`preview.html` 只是本地用的，**不会被 GitHub 渲染**，留着不碍事，也可以删掉。

---

## 3. 文件结构

```
.
├── README.md                  ← 主页本体（布局在这里）
├── assets/                    ← 全部是仓库自带的 SVG，不依赖外部图床
│   ├── banner-{light,dark}.svg     顶部横幅：黄昏天空 / 彗星 / 小镇 / 水面倒影
│   ├── card-{light,dark}.svg       简介卡片
│   ├── divider-{light,dark}.svg    章节之间的分隔装饰
│   ├── footer-{light,dark}.svg     页脚
│   ├── heatmap-{light,dark}.svg    贡献热力图（★ 每天自动重绘）
│   └── activity-{light,dark}.svg   提交节奏 + 统计（★ 每天自动重绘）
├── data/
│   └── contributions.json     ← 拉下来的原始贡献数据缓存（每天更新）
├── tools/
│   ├── build_assets.py        ← 装饰素材生成器（改配色就改这里，离线可用）
│   ├── build_heatmap.py       ← 贡献卡片生成器（拉数据 + 渲染）
│   └── render.sh              ← 把 SVG 渲染成 PNG，方便自己看效果（仅 macOS 用）
├── .github/workflows/
│   └── refresh-contributions.yml   ← 每天自动刷新上面那两张卡
├── extras/                    ← 可选增强，默认不生效，见 extras/README.md
└── preview.html               ← 本地预览页
```

**为什么图形要用自家 SVG？** 因为 GitHub 会过滤 README 里的 `<style>` 标签和内联 `style=""`，
纯靠 HTML/CSS 做不出渐变、发光、动画。但 **SVG 文件本身不会被过滤** ——
在 `.svg` 里面可以随便用渐变、`feGaussianBlur`、SMIL 动画。所以"好看"的部分全部放在 SVG 里。

---

## 4. 关于 GitHub 原生的热力图和 Contribution activity

这两块是**绕不过去的**，先说清楚：

| 位置 | 能不能改样式 |
|---|---|
| 主页顶部那块绿色格子热力图 | ❌ 完全不行。它是 GitHub 自己渲染的 UI，不读 README、不读 CSS、也不认主题 |
| 右侧 / 下方的 **Contribution activity** 动态流 | ❌ 改不了样式，但 ✅ **可以整个关掉** |
| 你自己仓库里的 "Insights → Contributors" 图 | ❌ 同上 |

**关掉 Contribution activity 的方法**（官方文档里的路径）：

1. 打开你的主页 → 在贡献图**上方**找到 **Contribution settings** 下拉菜单
2. 点 **Activity overview** 即可切换显示 / 隐藏

关掉之后主页会清爽很多，顶部是原生热力图，紧接着就是你自定义的横幅和卡片。

**想换配色怎么办？** 只能用「自己渲染」的办法 —— 也就是本项目做的：
把同一份贡献数据从公开 API 拉下来，用自己的配色重画一张 SVG，嵌进 README。
数据口径和 GitHub 一致（同一天、同一次提交都算），只是颜色是你说了算。

### 自己渲染的这两张卡是怎么工作的

| 文件 | 作用 |
|---|---|
| `tools/build_heatmap.py` | 拉数据 + 渲染两张卡（亮暗共 4 个 SVG） |
| `data/contributions.json` | 数据缓存，断网也能重绘 |
| `.github/workflows/refresh-contributions.yml` | 每天 UTC 02:23 自动重跑并提交 |

热力图的 5 个等级色在 `tools/build_assets.py` 的 `levels` 里，**越活跃越接近日落色**：

```python
"levels": ["#241a42", "#4a2a6b", "#8e3f7a", "#d9665f", "#ffc06a"],  # dark
"levels": ["#efe4f2", "#cda9de", "#e07ba8", "#ff9a5c", "#ffc93c"],  # light
```

改完跑：

```bash
python3 tools/build_heatmap.py            # 联网拉最新数据
python3 tools/build_heatmap.py --offline  # 用缓存重绘（调样式时用这个，秒出）
```

换成别的用户 / 别的年份：

```bash
python3 tools/build_heatmap.py --user someone-else
python3 tools/build_heatmap.py --years all        # 或 2025
```

三个注意点：

1. **卡片按 900px 宽设计**，不是随便定的。GitHub 正文栏约 880px，按 1200px 设计会被缩小 27%，
   图例数字和星期标签就糊了。要往里加内容，改 `CARD_W` 时记得把字号一起调大。
2. **Action 需要 `permissions: contents: write`**（已经写在 workflow 里了），否则提交会被拒。
3. **仓库连续 60 天没有任何活动时，GitHub 会自动停掉定时任务。** 这个 workflow 自己会提交，
   所以正常情况下会一直跑；真被停了，去 Actions 页面点一下 Enable 即可。

---

## 4. 改配色 / 改图形

所有颜色都集中在 `tools/build_assets.py` 顶部的 `P` 字典里，亮暗各一套：

```python
P = {
    "dark":  { "sky": [...], "comet_a": "#fff6d8", "name_a": "#fff2c2", ... },
    "light": { "sky": [...], "comet_a": "#fffdf2", "name_a": "#2b2a72", ... },
}
```

改完重新生成：

```bash
python3 tools/build_assets.py
```

会用固定的随机种子重绘星野、山脊、楼群和窗灯 —— **每次结果都一样**，不会越改越乱。

想调构图的话，`banner()` 里几个关键常量：

| 变量 | 作用 |
|---|---|
| `HORIZON` | 地平线位置（默认 300），调小 = 天空更多 |
| `comet_head` | 彗星头部坐标 |
| `comet_len` | 彗尾长度 |
| `cloud_spec` | 云的位置 / 大小 / 漂移速度 |
| `sun_y` / `sun_r` | 落日位置和大小 |

---

## 6. 你需要动手改的地方（搜 `TODO` 就能找到）

- **简介文案** —— `## 关于我` 下面那两段和四条 bullet，现在写的是通用的，换成你自己的
- **技术栈徽章** —— `## 工具箱`，删掉不用的、加你真正在用的
- **项目介绍** —— `## 精选`，`SkillForge` 的占位文案必须换掉（那个仓库现在 README 只有一行标题）
- **联系方式** —— 顶部徽章区有一段被我注释掉的 Email / Telegram / X，取消注释改成你的地址

徽章写法：

```
https://img.shields.io/badge/<名称>-<色号>?style=flat-square&logo=<图标名>&logoColor=white&labelColor=1a1035
```

图标名去 <https://simpleicons.org> 查。`labelColor=1a1035` 是这套主题的深紫底色，建议保留。

---

## 7. 用到的第三方服务

| 服务 | 用途 | 备注 |
|---|---|---|
| `github-contributions-api.jogruber.de` | **贡献原始数据**（热力图 / 节奏卡的唯一数据源） | 公开、无需 token。**只在构建时调用一次**，访客看到的 SVG 是仓库里现成的，不依赖它 |
| `readme-typing-svg.demolab.com` | 打字机效果标语 | 截图里会是空白，因为它从第 0 帧开始动画，实际页面上正常 |
| `github-readme-stats.vercel.app` | 统计卡 / 语言分布 | 仓库太新时可能显示为空，正常 |
| `streak-stats.demolab.com` | 连续提交天数 | 同上 |
| `komarev.com/ghpvc` | 访客计数 | |
| `img.shields.io` | 各种徽章 | |

这些都是公共免费服务，偶尔会抽风。**主页的主体（横幅 / 卡片 / 分隔 / 页脚 / 两张贡献卡）全是仓库
自带的 SVG，访客侧不依赖任何外部服务** —— 就算哪天全挂了，主页依然好看。
你要是想彻底不依赖外部服务，把 `## 数据` 整节删掉即可（`## 足迹` 那两张可以留着，它们是自带的）。

> 顺带一提，一开始我试过用 `github-readme-activity-graph.vercel.app` 来画活动曲线，
> **实测返回 HTTP 402**（免费额度已停），所以没有采用。

---

## 8. 亮暗主题是怎么切的

README 里每个图形都写成这样：

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img src="assets/banner-light.svg" alt="..." width="100%">
</picture>
```

GitHub 官方支持 `<picture>` + `prefers-color-scheme`，访客用什么主题就加载哪张图。
所以**每改一次配色，记得两套都要看一遍** —— 浅色主题下用的是深色文字，对比度要求和暗色完全不同。

---

## 9. 一些踩过的坑

- **别在 README 里用 `<style>` 或 `style="..."`** —— GitHub 会直接删掉，不起作用。
- **正文尽量别用 `<table>` 排版** —— GitHub 会给原始 HTML 表格加上边框，两栏布局会多出一圈线。
  这份 README 全程用 `<div align="center">` + 居中堆叠来排版，手机窄屏也不会挤。
- **`<img>` 的 `width` / `height` 属性是保留的**，用 `width="100%"` 让横幅自适应宽度。
- **SVG 里不加载外部字体**，用 `system-ui` / `Hiragino Sans` 这类系统字体栈，中文才不会掉成方块。
- **按正文栏宽设计，别按 1200px 设计。** GitHub 正文栏实际只有 **约 880px**，
  1200px 宽的图会被缩小 27%，小字号直接糊成一团。热力图那两张卡就是按 900px 画的。
- **SVG 里的 `<title>` 提示框在 GitHub 上不会弹。** 因为 README 是用 `<img>` 引用 SVG 的，
  这种上下文里 SVG 不接收鼠标事件，`<title>` 和 `:hover` 全部失效。
  所以热力图**不能只靠悬浮看数值** —— 图例必须印上数字区间（`0 / 1 / 2-3 / 4-6 / 7`），
  这也是无障碍的基本要求：不要让颜色成为唯一的区分手段。
- **贡献数据不是实时的**，Action 每天跑一次。刚提交完看不到变化是正常的，
  去 Actions 页面手动 Run workflow 就能立刻刷新。

---

## 10. 想再加点东西？

`extras/` 目录里放了两个可选增强，**默认不生效**（GitHub 只认 `.github/workflows/`）：

- **贡献贪吃蛇** —— 一条蛇在贡献格子上爬，配色已按黄昏主题调好，复制一个文件就能开
- **lowlighter/metrics** —— 想要语言环图、写代码时段分布、成就徽章等更多可视化时的方案

具体怎么开、各自的代价是什么，见 `extras/README.md`。
