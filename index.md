---
layout: default
title: 
---

<div class="home">

  <h1 class="page-heading">Jiahua's Birding</h1>

  <p>This is where I record my birding.</p>

  <!-- 第一部分：Banner图片 -->
  <!-- 这里的 class="u-photo" 是为了保持样式，也可以不加 -->
  <p>
    <img src="images/homepage.jpeg" alt="homepage" style="width:100%">
    <br>
    <em>Shot in Medog, April 2025</em>
  </p>

  <!-- 第二部分：文章列表 (Posts) - 我把它移到了这里 -->
  <h2 class="post-list-heading">Latest Trips</h2>
    <ul class="post-list">
      <!-- 注意这里加了 limit:3 -->
      {% for post in site.posts limit:1 %}
        <li>
          <span class="post-meta">{{ post.date | date: "%b %-d, %Y" }}</span>
          <h3>
            <a class="post-link" href="{{ post.url | relative_url }}">
              {{ post.title | escape }}
            </a>
          </h3>
        </li>
      {% endfor %}
    </ul>
  
    <!-- 加一个按钮引导大家去Blog页看更多 -->
    <p><a href="/blog/">View all posts &rarr;</a></p>

  <!-- 第三部分：足迹地图 (Footprint) - 现在它在下面了 -->
  <h2>Footprint</h2>
  <iframe src="https://www.google.com/maps/d/u/0/embed?mid=1aJE5c67qzWqcivA3QhWyrQC3i2ziK8o&ehbc=2E312F" width="640" height="480" style="border:none; max-width:100%;"></iframe>

</div>