# Yue Xiu（修越）个人主页

引用量由这台 Mac 的 `launchd` 任务每天 09:00 自动检查。当前系统时区为 `Asia/Shanghai`，对应北京时间。电脑需要开机、登录并联网；休眠期间错过的任务会在唤醒后补跑，登录时也会执行一次。Google Scholar 已在实际测试中拒绝 GitHub 云端运行器的请求，因此使用本机抓取。

任务在临时目录克隆 `main`，读取 Google Scholar 的总引用量和论文引用量，只更新 `_config.yml` 与 `_includes/about/publications.md` 中的引用数据。论文引用量大于 30 时显示徽标。数据变化后自动提交、推送，触发现有 Cloudflare Pages 部署流程并校验两个正式域名；没有变化则不提交、不部署。更新时间表示最近一次引用数据发生变化的日期。日常编辑的工作目录不会被修改。

抓取失败、页面不完整或已有徽标无法准确匹配时，任务失败并保留原数据。任务使用本机已有的 Git 登录凭据；部署继续使用已有的 `CLOUDFLARE_API_TOKEN`，无需新增密钥。

安装或重新安装定时任务：

```sh
python3 .github/scripts/install_citation_schedule.py
```

安装位置为 `~/Library/LaunchAgents/org.xiuyue.citations.plist`，程序、独立 Python 环境和运行日志位于 `~/Library/Application Support/xiuyue-citations/`。查看日志或立即执行：

```sh
tail -n 30 "$HOME/Library/Application Support/xiuyue-citations/update.log"
launchctl kickstart "gui/$(id -u)/org.xiuyue.citations"
```

本地只检查、不写入文件：

```sh
python3 -m pip install 'beautifulsoup4>=4.12,<5'
python3 .github/scripts/update_scholar_citations.py --check
```

卸载时先执行 `launchctl bootout "gui/$(id -u)/org.xiuyue.citations"`，再删除上述 plist 文件即可。
