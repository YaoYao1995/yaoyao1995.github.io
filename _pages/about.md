---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>
My research interest includes neural machine translation and computer vision. I have published more than 100 papers at the top international AI conferences with total google scholar citations <strong><span id='total_cit'>260000+</span></strong>.

{% include_relative includes/intro.md %}

{% include_relative includes/news.md %}

{% include_relative includes/pub_short.md %}

{% include_relative includes/pub.md %}

{% include_relative includes/honers.md %}

{% include_relative includes/others.md %}
