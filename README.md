<h1 align="center">Yue Xiu（修越）学术主页</h1>

<p align="center">Associate Professor · University of Electronic Science and Technology of China</p>

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

源代码仓库为 [yuexiu92/yuexiu92.github.io](https://github.com/yuexiu92/yuexiu92.github.io)，GitHub Pages 地址为 <https://yuexiu92.github.io/>。

GitHub Pages 从 `main` 分支的仓库根目录构建，推送更新后会自动重新发布。`_config.yml` 已配置根域名地址，`baseurl` 留空。使用自定义域名时，再添加对应的 `CNAME` 文件并调整站点配置。
