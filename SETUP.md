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
│   ├── activity-{light,dark}.svg   提交节奏 + 统计（★ 每天自动重绘）
│   └── projects-{light,dark}.svg   项目列表（★ 每天自动重绘）
├── data/
│   └── contributions.json     ← 拉下来的原始贡献数据缓存（每天更新）
├── tools/
│   ├── build_assets.py        ← 装饰素材生成器（改配色就改这里，离线可用）
│   ├── build_heatmap.py       ← 贡献卡片生成器（拉数据 + 渲染）
│   ├── build_projects.py      ← 项目卡生成器（About 字段 + 语言构成）
│   └── render.sh              ← 把 SVG 渲染成 PNG，方便自己看效果（仅 macOS 用）
├── .github/workflows/
│   └── refresh-contributions.yml   ← 每天自动刷新上面三张卡
├── extras/                    ← 可选增强，默认不生效，见 extras/README.md
└── preview.html               ← 本地预览页
```

**为什么图形要用自家 SVG？** 因为 GitHub 会过滤 README 里的 `<style>` 标签和内联 `style=""`，
纯靠 HTML/CSS 做不出渐变、发光、动画。但 **SVG 文件本身不会被过滤** ——
在 `.svg` 里面可以随便用渐变、`feGaussianBlur`、SMIL 动画。所以"好看"的部分全部放在 SVG 里。

---

## 4. README 下面那几块原生区块，到底能不能动

这是最容易被误解的地方。主页从上到下其实是**两个世界**：上面是你的 README（完全可控），
下面是 GitHub 自己渲染的固定区块（基本不可控）。

| 区块 | 能不能改 | 怎么办 |
|---|---|---|
| **Popular repositories**（置顶仓库卡） | ⚠️ 样式改不了，但**内容能改** | 卡片本身是 GitHub 的 UI；但「About 简介」是你填的。**简介为空 = 一张空白卡**，见下面第 5 节 |
| **绿色格子热力图** | ❌ 完全不行 | 不读 README、不读 CSS、不认主题。只能自己在 README 里重画一张同数据的卡（本项目已做） |
| **Activity overview**（含 "Contributed to …" 和执行摘要图） | ❌ 样式改不了，✅ **可以关掉** | 主页贡献图**上方** → **Contribution settings** 下拉 → 点 **Activity overview** |
| **Contribution activity**（按月的时间线 + Show more activity） | ❌ **官方不支持关闭** | 这是个长期未实现的 feature request，见 [community#43304](https://github.com/orgs/community/discussions/43304)。只能接受它 |
| **Achievements**（成就徽章） | ❌ 不行 | 同上 |

**关于 Activity overview**：关掉它能去掉那个绿色雷达图和 "Contributed to …" 列表，
主页会清爽不少。这是 GitHub 官方文档里写明的路径（见
[docs](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/showing-an-overview-of-your-activity-on-your-profile)）。

**关于 Contribution activity 时间线**：查过了，**没有开关**。GitHub 社区里
"Option to hide only contribution activities in Profile" 这个帖子至今仍是 feature request 状态。
所以那一大块深色时间线会一直留在主页最下面 —— 我们能做的只是把 README 做得足够好看，
让人先看到你设计过的部分。

### 数字为什么对不上：你的 28 vs 卡片的 23

GitHub 页面上写「28 contributions in the last year」，而我们的卡片写「23 次公开提交」。

**两个都对**，只是口径不同：

- GitHub 那个数字 **含私有贡献**（你的 Activity overview 里出现了 `RoostBase/RoostAI`，
  那是个私有仓库）—— 只有你登录后才看得到这部分
- 公开 API 只能拿到 **公开** 贡献，未登录的访客看到的也是 23

所以卡片上专门标了「**公开提交**」四个字，避免访客觉得数字不对。想让它更接近，
可以在 **Settings → Public profile → Contributions & Activity** 里调整私有贡献的显示方式。

**想换配色怎么办？** 只能用「自己渲染」的办法 —— 也就是本项目做的：
把同一份贡献数据从公开 API 拉下来，用自己的配色重画一张 SVG，嵌进 README。
数据口径和 GitHub 一致（同一天、同一次提交都算），只是颜色是你说了算。

### 自己渲染的这三张卡是怎么工作的

| 文件 | 作用 |
|---|---|
| `tools/build_heatmap.py` | 拉贡献数据 + 渲染热力图 / 节奏卡 |
| `tools/build_projects.py` | 读各仓库 About 字段 + 渲染项目卡（含语言构成条） |
| `data/contributions.json` | 数据缓存，断网也能重绘 |
| `.github/workflows/refresh-contributions.yml` | 每天 UTC 02:23 自动重跑并提交 |

### 为什么把第三方统计卡全删了

早期版本里有 `github-readme-stats` 和 `streak-stats` 两张卡。删掉的原因是
**同一页面上出现了互相矛盾的「提交数」**：

| 来源 | 显示 |
|---|---|
| 我的热力图卡 | 23 |
| GitHub 原生 | 24 |
| `streak-stats` | 26 |
| `github-readme-stats` | Total Commits 2 |

四个数字、三种口径，访客无法判断该信哪个。而且 `github-readme-stats` 还会给一个
「C」等级 —— 一个只有几次提交的账号被评 C，既不准也不好看。

**现在的原则：任何统计数字只有一个出处。** 具体做法：

1. **数据源换成 GitHub 自己的贡献日历**（`github.com/users/<user>/contributions`）。
   它才是权威来源，数字和主页上那个**逐一对得上**。
   原来用的第三方 JSON API 会缓存、可能滞后一天，所以才会差 1。
   第三方 API 现在只作备用（GitHub 页面结构变了就用它兜底）。
2. **删除 `streak-stats`** —— 连续天数我的「提交节奏」卡里已经有了。
3. **删除 `github-readme-stats` 主卡** —— 提交数重复，其余是 star / PR / issue（目前都是 0）。
4. **语言构成改由自己渲染**（`build_projects.py` 里的堆叠色条），
   替掉第三方的 top-languages 卡，样式和其余卡片完全统一。

结果：**主页上除了徽章、打字机标语和访客计数，没有任何第三方数据卡**，
所有图形都是仓库里的 SVG。

> 想把某张卡加回来也可以，但加之前先想清楚：它显示的数字会不会和已有卡片打架。

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

### 修好那两张空白的置顶仓库卡

你的两个仓库 **About 简介都是空的**，所以主页上的置顶卡看起来像坏了 ——
`SkillForge` 是一整块空白，`ilovfyu` 只有一个 "Python"。

**这个改起来很快，收益却很大**，因为置顶卡是主页上面积第二大的元素。

改法：打开仓库首页，点右侧 **About** 栏右上角的**齿轮图标**，填：

| 仓库 | Description（可直接复制） | Topics 建议 |
|---|---|---|
| `SkillForge` | 把零散的想法锻造成可复用的技能模块 —— 轻量的技能编排与执行框架。 | `python` `cli` `tooling` |
| `ilovfyu` | 我的 GitHub 主页：黄昏主题、全手写 SVG、每天自动刷新的贡献卡片。 | `profile-readme` `svg` `github-actions` |

> 上面 `SkillForge` 那句是我按名字猜的，**请改成真实的一句**。
> 一句话说清「谁在什么场景下会用到它」就够，别写成功能清单。

改完之后做两件事：

1. **排列置顶**：主页 → **Customize your pins** → 勾选要展示的仓库并拖成想要的顺序。
   建议 `SkillForge` 放第一；`ilovfyu`（主页仓库本身）可以放第二，也可以不置顶。
2. **刷新项目卡**：`tools/build_projects.py` 读的就是这个 About 字段，
   下次 Action 跑完（或手动 Run workflow 一次）简介就会自动出现在卡片上。

本地想立刻看效果：

```bash
python3 tools/build_projects.py
```

简介为空时它会打印警告，明确告诉你哪个仓库还没写：

```
  ! ilovfyu/SkillForge 没有写 About 简介 —— 首页卡片上会是空的，建议补上
```

---

## 5. 改配色 / 改图形

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
