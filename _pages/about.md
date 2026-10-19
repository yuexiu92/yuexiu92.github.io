---
permalink: /
title: ""
excerpt: "Yue Xiu (修越), Postdoctoral Researcher at UESTC. Large language models, agentic AI, efficient learning and inference, and AI systems for wireless networks."
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% include bilingual-section.html file="intro" id="about-me" icon="person" title="About Me" title_zh="个人简介" %}

<div class="section-card career-grid">
{% include bilingual-section.html file="education" id="education" icon="graduation" title="Education" title_zh="教育经历" class="career-section" %}
{% include bilingual-section.html file="experience" id="experience" icon="briefcase" title="Experience" title_zh="工作经历" class="career-section" %}
</div>

{% capture publications %}{% include about/publications.md %}{% endcapture %}
<section class="section-card publications-section" aria-labelledby="publications">
{{ publications | markdownify }}
</section>

{% include bilingual-section.html file="projects" id="projects" icon="folder" title="Selected Projects" title_zh="科研项目" %}

{% include bilingual-section.html file="service" id="service" icon="people" title="Academic Service" title_zh="学术服务" %}
