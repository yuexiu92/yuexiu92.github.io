# Yue Xiu（修越）个人主页

引用量由 [Update Google Scholar citations](https://github.com/yuexiu92/yuexiu92.github.io/actions/workflows/update-citations.yml) 工作流每天北京时间 09:00 自动检查，也可在该页面点击 **Run workflow** 立即执行。

任务读取 Google Scholar 的总引用量和论文引用量，只更新 `_config.yml` 与 `_includes/about/publications.md` 中的引用数据。论文引用量大于 30 时显示徽标。数据变化后自动提交到 `main`，调用已有 Cloudflare Pages 部署流程，并校验两个正式域名；没有变化则不提交、不部署。更新时间表示最近一次引用数据发生变化的日期。

抓取失败、页面不完整或已有徽标无法准确匹配时，任务失败并保留原数据。可在 Actions 页面查看日志。任务使用仓库的 `GITHUB_TOKEN`，部署继续使用已有的 `CLOUDFLARE_API_TOKEN`，无需新增密钥。

本地只检查、不写入文件：

```sh
python3 -m pip install 'beautifulsoup4>=4.12,<5'
python3 .github/scripts/update_scholar_citations.py --check
```

GitHub 的定时任务可能延迟；公开仓库连续 60 天没有活动时，GitHub 会停用定时工作流，可在 Actions 页面重新启用。参见 [GitHub 定时任务说明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。
