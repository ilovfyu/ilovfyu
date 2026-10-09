# 可选增强 · Extras

这个目录里的东西**默认不会生效** —— 因为 GitHub 只认 `.github/workflows/*.yml`。
想要哪个，把文件复制过去再提交就行；不想要就整个目录删掉，不影响任何东西。

---

## 1. 贡献贪吃蛇（snake.yml）

一条贪吃蛇在你的贡献格子上爬，吃掉有提交的格子。是 GitHub 主页最经典的热力图玩法之一。

```bash
cp extras/snake.yml .github/workflows/snake.yml
git add .github/workflows/snake.yml && git commit -m "chore: enable snake" && git push
```

它会在 Actions 里跑一次，把结果推到 `output` 分支。**第一次跑完**之后，在 README 的
`## 足迹` 章节里加上这段（`ilovfyu/ilovfyu` 是仓库名）：

```html
<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)"
          srcset="https://raw.githubusercontent.com/ilovfyu/ilovfyu/output/snake-dark.svg">
  <img alt="贡献贪吃蛇动画" width="100%"
       src="https://raw.githubusercontent.com/ilovfyu/ilovfyu/output/snake-light.svg">
</picture>
</div>
```

配色已经按黄昏主题调好了，`color_dots` 的 5 个色号就是热力图那 5 级：

| 主题 | 色号（由浅到深 = 越活跃） |
|---|---|
| light | `#efe4f2` `#cda9de` `#e07ba8` `#ff9a5c` `#ffc93c` |
| dark | `#241a42` `#4a2a6b` `#8e3f7a` `#d9665f` `#ffc06a` |

> 注意：贪吃蛇用的是 GitHub 的公开贡献格子，配色参数见
> [Platane/snk](https://github.com/Platane/snk)。它不是实时数据，每天跑两次。

---

## 2. lowlighter/metrics（更重的方案）

如果你想要**更多**的可视化 —— 语言占比环图、习惯（几点写代码）、最常用的表情、
成就徽章、等距贡献日历 —— [lowlighter/metrics](https://github.com/lowlighter/metrics)
是最强的选择。它同样跑在 Actions 里，输出一张（或几张）完全可控样式的 SVG。

它的贡献日历插件 `isocalendar` 也能直接换色：

```yaml
- uses: lowlighter/metrics@latest
  with:
    token: ${{ secrets.METRICS_TOKEN }}
    base: ""
    plugin_isocalendar: yes
    plugin_isocalendar_duration: full-year
    config_timezone: Asia/Shanghai
    # 颜色用 CSS 变量注入到生成的 SVG 里
    extras_css: |
      .calendar .day { fill: #241a42; }
```

**为什么我没有默认给你装上**：它需要一个 PAT（`secrets.METRICS_TOKEN`）而不是默认
`GITHUB_TOKEN`，生成的 SVG 体量大、样式靠 CSS 注入容易随版本变动，而且一旦服务端改版
你的卡片就可能变形。相比之下 `tools/build_heatmap.py` 是你自己仓库里的代码，
坏了自己能修，配色和数据口径也完全可控。

想上就上，但建议先看看它的实际效果再决定。

---

## 3. 为什么不直接用别人的热力图服务

试过的几个：

| 服务 | 结果 |
|---|---|
| `github-readme-activity-graph.vercel.app` | **返回 HTTP 402**（免费额度已停），实测不可用 |
| `ghchart.rshah.org` | 只支持单一颜色，没有分级、没有图例 |
| `github-readme-stats` | 没有专门的热力图卡片，只有总计/语言 |

所以最后是自己渲染 —— 五个等级、数值图例、中英双语标签，全部跟着主题走。
