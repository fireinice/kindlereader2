TEMPLATES = {}
TEMPLATES['content.html'] = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>{{ user['userName'] }}'s Daily Digest</title>
<style type="text/css">
body{
font-size: 1.1em;
margin:0 5px;
}
h1{
font-size:4em;
font-weight:bold;
}
h2 {
font-size: 1.2em;
font-weight: bold;
margin:0;
}
a {
color: inherit;
text-decoration: inherit;
cursor: default
}
a[href] {
color: blue;
text-decoration: underline;
cursor: pointer
}
p{
text-indent:1.5em;
line-height:1.3em;
margin-top:0;
margin-bottom:0;
}
.italic {
font-style: italic
}
.do_article_title{
line-height:1.5em;
page-break-before: always;
}
#cover{
text-align:center;
}
#toc{
page-break-before: always;
}
#content{
margin-top:10px;
page-break-after: always;
}
</style>
</head>
<body>
  <div id="cover">
    <h1 id="title">{{ user['userName'] }}'s Daily Digest</h1>
    <a href="#content">Go straight to first item</a><br />
    {{ datetime.datetime.utcnow().strftime("%m/%d %H:%M") }}
  </div>
  <div id="toc">
    <h2>Feeds:</h2>
    <ol>
      {% set feed_count = 0 %}
      {% set feed_idx=0 %}
      {% for feed in feeds %}
        {% set feed_idx=feed_idx+1 %}
        {% if feed.item_count > 0 %}
          {% set feed_count = feed_count + 1 %}
          <li>
            <a href="#sectionlist_{{ feed_idx }}">{{ feed.title }}</a>
            <br />
            {{ feed_count > 0 }} items
          </li>
        {% end %}
      {% end %}
    </ol>
    {% set feed_idx=0 %}
    {% for feed in feeds %}
      {% set feed_idx=feed_idx+1 %}
      {% if feed.item_count > 0 %}
        <mbp:pagebreak />
        <div id="sectionlist_{{ feed_idx }}" class="section">
          {% if feed_idx < feed_count %}
            <a href="#sectionlist_{{ feed_idx+1 }}">Next Feed</a> |
          {% end %}
          {% if feed_idx > 1 %}
            <a href="#sectionlist_{{ feed_idx-1 }}">Previous Feed</a> |
          {% end %}
          <a href="#toc">TOC</a> |
          {{ feed_idx }}/{{ feed_count }} |
          {{ feed.item_count }} items
          <br />
          <h3>{{ feed.title }}</h3>
          <ol>
            {% set item_idx=0 %}
            {% for item in feed.items %}
              {% set item_idx=item_idx+1 %}
              <div id="articleSignal_{{ feed_idx }}_{{ item_idx }}">
                <li>
                  <a href="#article_{{ feed_idx }}_{{ item_idx }}">{{ item.title }}</a><br/>
                  {% if item.published %}{{ item.published }}{% end %}
                </li>
              </div>
            {% end %}
          </ol>
        </div>
      {% end %}
    {% end %}
  </div>
  <mbp:pagebreak />
  <div id="content">
    {% set feed_idx=0 %}
    {% for feed in feeds %}
      {% set feed_idx=feed_idx+1 %}
      {% if feed.item_count > 0 %}
        <div id="section_{{ feed_idx }}" class="section">
          {% set item_idx=0 %}
          {% for item in feed.items %}
            {% set item_idx=item_idx+1 %}
            <div id="article_{{ feed_idx }}_{{ item_idx }}" class="article">
              <h2 class="do_article_title">
                {% if item.url %}
                  <a href="{{ item.url }}">{{ item.title }}</a>
                {% else %}
                  {{ item.title }}
                {% end %}
              </h2>
              {% if item.published %}{{ item.published }}{% end %}
              <a href="#articleSignal_{{ feed_idx }}_{{ item_idx }}">Return Feed</a>
              &nbsp;&nbsp;
              {% set pocket_url = pocket.getPocketInfo(item.url, item.title) %}
              {% if pocket_url %}<a href="{{ pocket_url }}">Send to Pocket</a>{% end %}
              <div>{{ item.content }}</div>
              <a href="#articleSignal_{{ feed_idx }}_{{ item_idx }}">Return Feed</a>
              &nbsp;&nbsp;
              {% if pocket_url %}<a href="{{ pocket_url }}">Send to Pocket</a>{% end %}
              &nbsp;&nbsp;
              {% if feed.item_count == item_idx %}
                {% set mark_read_url = read_marker.getMarkItemsReadURL(feed) %}
                <a href="{{mark_read_url }}">Mark Above Items In Feed As Read</a>
              {% end %}
            </div>
          {% end %}
        </div>
      {% end %}
    {% end %}
  </div>
</body>
</html>

"""
TEMPLATES['toc.ncx'] = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="zh-CN">
<head>
<meta name="dtb:depth" content="4" />
<meta name="dtb:totalPageCount" content="0" />
<meta name="dtb:maxPageNumber" content="0" />
</head>
<docTitle><text>{{ user['userName'] }}'s Daily Digest</text></docTitle>
<docAuthor><text>{{ user['userName'] }}</text></docAuthor>
<navMap>
{% if format == 'periodical' %}
<navPoint class="periodical">
<navLabel><text>{{ user['userName'] }}'s Daily Digest</text></navLabel>
<content src="content.html" />
{% set feed_idx=0 %}
{% for feed in feeds %}
{% set feed_idx=feed_idx+1 %}
{% if feed.item_count > 0 %}
<navPoint class="section" id="{{ feed_idx }}">
<navLabel><text>{{ escape(feed.title) }}</text></navLabel>
<content src="content.html#section_{{ feed_idx }}" />
    {% set item_idx=0 %}
    {% for item in feed.items %}
      {% set item_idx=item_idx+1 %}
      <navPoint class="article" id="{{ feed_idx }}_{{ item_idx }}" playOrder="{{ item_idx }}">
        <navLabel><text>{{ escape(item.title) }}</text></navLabel>
        <content src="content.html#article_{{ feed_idx }}_{{ item_idx }}" />
        {% if item.author %}<mbp:meta name="author">{{ item.author }}</mbp:meta> {% end %}
      </navPoint>
    {% end %}
</navPoint>
{% end %}
{% end %}
</navPoint>
{% else %}
<navPoint class="book">
<navLabel><text>{{ user['userName'] }}'s Daily Digest</text></navLabel>
<content src="content.html" />
{% set feed_idx=0 %}
{% for feed in feeds %}
{% set feed_idx=feed_idx+1 %}
{% if feed.item_count > 0 %}
{% set item_idx=0 %}
{% for item in feed.item_count %}
  {% set item_idx=item_idx+1 %}
    <navPoint class="chapter" id="{{ feed_idx }}_{{ item_idx }}" playOrder="{{ item_idx }}">
<navLabel><text>{{ escape(item.title) }}</text></navLabel>
<content src="content.html#article_{{ feed_idx }}_{{ item_idx }}" />
</navPoint>
{% end %}
{% end %}
{% end %}
</navPoint>
{% end %}
</navMap>
</ncx>
"""
TEMPLATES['content.opf'] = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
<metadata>
<dc-metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
{% if format == 'periodical' %}
<dc:title>{{ user['userName'] }}'s Daily Digest</dc:title>
{% else %}
<dc:title>{{ user['userName'] }}'s Daily Digest({{ datetime.datetime.utcnow().strftime("%m/%d %H:%M") }})</dc:title>
{% end %}
<dc:language>zh-CN</dc:language>
<dc:identifier id="uid">{{ user['userName'] }}{{ datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") }}</dc:identifier>
<dc:creator>kindlereader</dc:creator>
<dc:publisher>kindlereader</dc:publisher>
<dc:subject>{{ user['userName'] }}'s Daily Digest</dc:subject>
<dc:date>{{ datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") }}</dc:date>
<dc:description></dc:description>
</dc-metadata>
{% if format == 'periodical' %}
<x-metadata>
<output encoding="utf-8" content-type="application/x-mobipocket-subscription-magazine"></output>
</x-metadata>
{% end %}
</metadata>
<manifest>
<item id="content" media-type="application/xhtml+xml" href="content.html"></item>
<item id="toc" media-type="application/x-dtbncx+xml" href="toc.ncx"></item>
</manifest>
<spine toc="toc">
<itemref idref="content"/>
</spine>
<guide>
<reference type="start" title="start" href="content.html#content"></reference>
<reference type="toc" title="toc" href="content.html#toc"></reference>
<reference type="text" title="cover" href="content.html#cover"></reference>
</guide>
</package>
"""
