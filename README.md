# 苏俊通 · Juntong Su

[中文主页](https://large-su.github.io/) · [English homepage](https://large-su.github.io/en/)

个人学术主页，使用 GitHub Pages 从 `main` 分支的 `/docs` 目录发布。

## 更新内容

在 `content/site.json` 中维护个人简介、研究方向、论文、专利和学术会议。`zh` 和 `en` 分别存放两种语言的内容。论文列表按出版年份排列，带 `summary` 的条目同时显示在首页的代表论文区域。`events` 可以用 `paper` 关联一篇论文，也可以用双语 `description` 记录报告或活动。

修改后运行以下命令。构建脚本用同一份数据生成两个语言版本，使用 Python 标准库。

```powershell
python build.py
python -m http.server 8765 --bind 127.0.0.1 --directory docs
```

浏览 `http://127.0.0.1:8765/` 检查中文主页，英文页在 `/en/`。提交 `content/site.json` 和生成后的 `docs/` 文件，再推送至 `main` 触发 Pages 更新。样式与论文筛选脚本位于 `docs/assets/`。

## 资料与配图

论文条目通过 DOI 指向出版社，专利和会议条目附各自的公开记录链接。首页的机器人铣削图为 ImageGen 生成的场景示意。Instrument Serif 和 Source Sans 3 字体随站点提供，许可文件位于 `docs/assets/`。
