---
layout: home
title: Jiahua's Birding
description: Birding journal and trip notes from China — the cloud forests of Medog, the winter steppe of Inner Mongolia, and everywhere the birds lead.
image: /images/homepage.jpeg
hero:
  image: /images/homepage.jpeg
  image_sm: /images/homepage-sm.jpg
  image_alt: "Clouds pouring over forested ridges in Medog, Tibet"
  kicker: "Birding journal · China"
  heading: "Jiahua's Birding"
  subtitle: "Field notes from the edge — the cloud forests of Medog, the winter steppe of Inner Mongolia, and the long look through binoculars in between."
  caption: "Medog, Tibet · April 2025"
facts:
  - value: "1,150+"
    label: "Species on my China list"
  - value: "6"
    label: "Lifers in Hailar"
  - value: "2025"
    label: "Medog, Tibet"
---

{% assign latest = site.posts.first %}

<section class="hero">
  <div class="hero__media">
    <img src="{{ page.hero.image | relative_url }}"
      {% if page.hero.image_sm %}srcset="{{ page.hero.image_sm | relative_url }} 1200w, {{ page.hero.image | relative_url }} 2400w" sizes="100vw"{% endif %}
      alt="{{ page.hero.image_alt }}" width="2400" height="1800" fetchpriority="high">
  </div>

  <div class="hero__inner">
    <p class="hero__kicker">{{ page.hero.kicker }}</p>
    <h1>{{ page.hero.heading }}</h1>
    <p class="hero__sub">{{ page.hero.subtitle }}</p>

    <div class="hero__foot">
      <span>{{ page.hero.caption }}</span>
      <a class="hero__scroll" href="#latest">
        Latest field notes
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 4v15m0 0 5.5-5.5M12 19l-5.5-5.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </a>
    </div>
  </div>
</section>

{% if page.facts %}
<section class="facts" aria-label="At a glance">
  <div class="wrap facts__grid">
    {% for fact in page.facts %}
      <div class="fact">
        <span class="fact__value">{{ fact.value }}</span>
        <span class="fact__label">{{ fact.label }}</span>
      </div>
    {% endfor %}
  </div>
</section>
{% endif %}

<section class="section" id="latest">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <div>
        <p class="eyebrow">Latest field notes</p>
        <h2>Recently in the field</h2>
      </div>
      <a class="text-link" href="{{ '/blog/' | relative_url }}">All field notes <span aria-hidden="true">&rarr;</span></a>
    </div>

    {% if latest %}
      <article class="feature" data-reveal>
        <a class="feature__media" href="{{ latest.url | relative_url }}">
          <img src="{{ latest.cover | relative_url }}"
            {% if latest.cover_sm %}srcset="{{ latest.cover_sm | relative_url }} 900w, {{ latest.cover | relative_url }} 1800w" sizes="(max-width: 900px) 92vw, 55vw"{% endif %}
            alt="{{ latest.cover_alt | default: latest.title | escape }}" width="1800" height="1350" loading="lazy">
          <span class="badge">{{ latest.season | default: "Latest trip" }}</span>
        </a>

        <div class="feature__body">
          <p class="meta-line meta-line--stack">
            <time datetime="{{ latest.date | date_to_xmlschema }}">{{ latest.date | date: "%B %-d, %Y" }}</time>
            {% if latest.location %}<span>{{ latest.location }}</span>{% endif %}
          </p>
          <h3><a href="{{ latest.url | relative_url }}">{{ latest.title | escape }}</a></h3>
          <p>{{ latest.excerpt | strip_html | normalize_whitespace }}</p>

          {% if latest.trip %}
            <ul class="trip-facts">
              {% for item in latest.trip limit:2 %}
                <li><b>{{ item.value }}</b><small>{{ item.label }}</small></li>
              {% endfor %}
            </ul>
          {% endif %}

          <a class="btn" href="{{ latest.url | relative_url }}">Read the field notes <span aria-hidden="true">&rarr;</span></a>
        </div>
      </article>
    {% else %}
      <p class="lede">No field notes yet — the first trip is on its way.</p>
    {% endif %}
  </div>
</section>

<section class="section section--tint">
  <div class="wrap split">
    <figure class="split__media" data-reveal>
      <img src="{{ '/images/about.jpg' | relative_url }}"
        srcset="{{ '/images/about-sm.jpg' | relative_url }} 640w, {{ '/images/about.jpg' | relative_url }} 1200w" sizes="(max-width: 900px) 92vw, 40vw"
        alt="Jiahua Xing in the field with a spotting scope and tripod" width="1200" height="1200" loading="lazy">
      <figcaption>In the field, somewhere between one bird and the next.</figcaption>
    </figure>

    <div class="split__body" data-reveal>
      <p class="eyebrow">About</p>
      <h2>A life measured in birds.</h2>
      <blockquote>The best bird of any trip is usually the one you didn't plan for.</blockquote>
      <p>I'm Jiahua Xing, a PhD candidate and birder based in China. This is where I keep the trips, the photographs, and the small moments that never fit on a checklist.</p>
      <p><a class="btn btn--ghost" href="{{ '/about/' | relative_url }}">More about me</a></p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <div>
        <p class="eyebrow">Footprint</p>
        <h2>Where the birds have taken me</h2>
      </div>
      <p class="lede">Every pin is a trip, and every trip began with a name on a list. The map is still filling in.</p>
    </div>

    <div class="map-frame" data-reveal>
      <iframe title="Map of my birding footprint" src="https://www.google.com/maps/d/u/0/embed?mid=1aJE5c67qzWqcivA3QhWyrQC3i2ziK8o&ehbc=2E312F" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>

    <div class="map-note">
      <span>Field trips across China, mapped as they happen.</span>
      <a class="text-link" href="https://www.google.com/maps/d/viewer?mid=1aJE5c67qzWqcivA3QhWyrQC3i2ziK8o" target="_blank" rel="noopener">Open the full map <span aria-hidden="true">&#8599;</span></a>
    </div>
  </div>
</section>
