# 苏俊通 · Juntong Su

[中文主页](https://large-su.github.io/) · [English homepage](https://large-su.github.io/en/)

个人学术主页，使用 GitHub Pages 从 `main` 分支的 `/docs` 目录发布。

## 更新内容

在 `content/site.json` 中维护个人简介、研究方向、场景、论文、专利和学术会议。`zh` 和 `en` 分别存放两种语言的内容。论文列表按出版年份排列，带 `summary` 的条目同时显示在首页的代表论文区域。`events` 可以用 `paper` 关联一篇论文，也可以用双语 `description` 记录报告或活动。

每篇论文在 `content/paper-details.json` 有一条同 ID 的记录，存放双语摘要概述 `overview` 和主要贡献 `contributions`。构建时生成两种语言的论文详情页，推荐引用使用 `site.json` 中的原始题名、作者和 DOI。

修改后运行以下命令。构建脚本用同一份数据生成两个语言版本，使用 Python 标准库。

```powershell
python build.py
python -m http.server 8778 --bind 127.0.0.1 --directory docs
```

浏览 `http://127.0.0.1:8778/` 检查中文主页，英文页在 `/en/`。提交 `content/` 中修改的数据和生成后的 `docs/` 文件，再推送至 `main` 触发 Pages 更新。样式与论文筛选脚本位于 `docs/assets/`。

## 资料与配图

论文条目通过 DOI 指向出版方，专利和会议条目附各自的公开记录链接。个人照片由苏俊通提供。DM Sans 和 Source Sans 3 字体随站点提供，许可文件位于 `docs/assets/`。
