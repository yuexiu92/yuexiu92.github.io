<h1 align="center">Yue Xiu（修越）学术主页</h1>

<p align="center">Postdoctoral Researcher · University of Electronic Science and Technology of China</p>

## 内容结构

- `_pages/about.md` 是主页入口，通过 `_includes/about/` 中的 Markdown 片段组合个人简介、论文、任职、教育经历和学术服务。
- 主页信息和代表性论文依据提供的 Yue Xiu 简历整理，包含任职、研究项目、教育经历和学术服务。
- `_config.yml` 管理姓名、机构、邮箱、Google Scholar 和部署地址；`images/yue-xiu.jpg` 是主页使用的头像。
- `_data/navigation.yml` 管理顶部导航。
- 顶部「中文 / English」按钮切换整页语言，默认英文，并在本地保存选择。英文正文位于 `_includes/about/`，中文译文位于 `_includes/about/zh/`；论文书目信息保留原文。
- Projects 单独展示简历中的科研项目，内容在 `_includes/about/projects.md`。
- 栏目和标题样式参考 [Steven 的 Academic Homepage Template](https://github.com/steven068zzy/academic-homepage-template)，使用以电子科技大学蓝为主的静态配色；布局样式在 `_sass/_academic.scss`，明暗配色在 `_sass/_dark-mode.scss`。
- 英文字体采用本地加载的 Source Sans 3，正文为 400、标题为 600；中文优先使用苹方、微软雅黑等系统字体。字体资源与开源许可证位于 `assets/fonts/source-sans-3/`。
- 图标暂用苹果风格的圆角线条 SVG，统一定义在 `_includes/icon.html`，样式在 `_sass/_icons.scss`，可在这两处集中替换。

## 本地预览

项目使用 Ruby 3.3。macOS 使用 Homebrew 时，可按下面的方式准备环境：

```bash
brew install ruby@3.3
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"
bundle install
./run_server.sh
```

打开终端中显示的本地地址即可预览。页面内容和样式会自动刷新；修改 `_config.yml` 后需要重启本地服务。

## 部署

主页已通过 Direct Upload 部署到 Cloudflare Pages，项目为 `xiuyue-homepage`，正式地址为 <https://www.xiuyue.org/>，备用地址为 <https://xiuyue-homepage.pages.dev/>。根域名 `xiuyue.org` 的 HTTP 和 HTTPS 请求会以 302 跳转至 `https://www.xiuyue.org/`，并保留访问路径。源代码继续保存在 [yuexiu92/yuexiu92.github.io](https://github.com/yuexiu92/yuexiu92.github.io)。

网站托管已迁至 Cloudflare；DNS 仍由 Squarespace 管理，DNSSEC 已开启，Google Workspace 的 MX、SPF 和 DKIM 记录已保留。完整 DNS 迁移仍待后续处理。

当前工作流是：本地修改 → 本地预览 → 提交并推送 GitHub 的 `main` 分支 → GitHub Actions 自动构建 → 发布到现有 Cloudflare Pages 项目。

自动发布配置位于 [`.github/workflows/cloudflare-pages.yml`](.github/workflows/cloudflare-pages.yml)。构建完成后，工作流上传生成的网页文件，正式地址和备用地址会一起更新。可以在 GitHub 仓库的 **Actions → Deploy to Cloudflare Pages** 查看进度；也可以使用 **Run workflow**，选择 `main` 手动重发。

`zsh push.sh` 执行 `git add .`、`git commit` 和 `git push`；推送成功后由 GitHub Actions 负责构建和发布。脚本会提交当前所有改动，运行前先用 `git diff` 检查。

首次配置需要在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中保存名为 `CLOUDFLARE_API_TOKEN` 的发布密钥。令牌只授予现有 Cloudflare 账户的 **Cloudflare Pages → Edit** 权限；账户 ID 已写入工作流，不需要额外的账户 ID 密钥。不要把令牌写进源文件或提交到 Git。

自动发布使用 Cloudflare 的 HTTPS 服务，无需等待 GitHub Pages 的自定义域名证书。

需要手动发布时，仍可在仓库根目录构建并打包：

```bash
JEKYLL_ENV=production bundle exec jekyll build --destination /private/tmp/xiuyue-cloudflare-site
rm -f /private/tmp/xiuyue-cloudflare-site/CNAME /private/tmp/xiuyue-cloudflare-site.zip
cd /private/tmp/xiuyue-cloudflare-site
zip -r /private/tmp/xiuyue-cloudflare-site.zip .
```

只删除上传目录中生成的 `CNAME`，保留仓库中的原文件。ZIP 根目录应直接包含 `index.html`、`assets/`、`images/` 等网站文件。

在 Cloudflare 控制台进入 **Workers & Pages → xiuyue-homepage → Create deployment**，上传 ZIP，选择 **Production** 并部署。完成后打开公开地址检查页面。
