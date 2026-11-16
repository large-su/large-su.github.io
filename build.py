"""Build the Chinese and English GitHub Pages site using the Python standard library."""

import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "docs"
DATA = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))

LABELS = {
    "zh": {
        "skip": "跳到正文",
        "navigation": "主要栏目",
        "language": "语言",
        "research": "研究方向",
        "selected": "代表论文",
        "publications": "论文",
        "patents": "专利",
        "events": "学术会议",
        "benchmark": "开放基准",
        "view_benchmark": "查看基准仓库",
        "doi": "期刊原文",
        "proceedings": "会议论文",
        "patent_record": "查阅公布文本",
        "keywords": "按题名、作者或 DOI 搜索",
        "results": "找到 {count} 篇论文",
        "no_results": "没有匹配的论文。",
        "all": "全部",
        "filter": "按研究方向筛选论文",
        "first": "第一作者",
        "co-first": "共同第一作者",
        "coauthor": "合著",
        "grant": "发明专利授权",
        "application": "发明专利申请公开",
        "inventors": "发明人",
        "top": "返回顶部",
        "updated": "更新于",
    },
    "en": {
        "skip": "Skip to content",
        "navigation": "Main navigation",
        "language": "Language",
        "research": "Research",
        "selected": "Selected papers",
        "publications": "Publications",
        "patents": "Patents",
        "events": "Conferences",
        "benchmark": "Open benchmark",
        "view_benchmark": "Explore the benchmark",
        "doi": "Journal article",
        "proceedings": "Conference paper",
        "patent_record": "View patent document",
        "keywords": "Search title, author, or DOI",
        "results": "{count} publications",
        "no_results": "No publications match your search.",
        "all": "All topics",
        "filter": "Filter publications by research topic",
        "first": "First author",
        "co-first": "Co-first author",
        "coauthor": "Co-author",
        "grant": "Granted invention patent",
        "application": "Published invention patent application",
        "inventors": "Inventors",
        "top": "Back to top",
        "updated": "Updated",
    },
}


def text(value):
    return escape(str(value), quote=True)


def local(value, language):
    return text(value[language])


def month(value, language, *, with_day=False):
    day = date.fromisoformat(value)
    if language == "zh":
        suffix = f"{day.day}日" if with_day else ""
        return f"{day.year}年{day.month}月{suffix}"
    if with_day:
        return f"{day.day} {day:%b %Y}"
    return day.strftime("%b %Y")


def arrow(symbol="↗"):
    return f'<span aria-hidden="true">{symbol}</span>'


def link(label, url, *, css="text-link", external=False, icon=""):
    external_attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
    return f'<a class="{css}" href="{text(url)}"{external_attrs}>{text(label)}{arrow(icon) if icon else ""}</a>'


def shown_names(names, person):
    selected = set(person["name"].values())
    return ", ".join(f"<strong>{text(name)}</strong>" if name in selected else text(name) for name in names)


def doi_link(paper):
    return "https://doi.org/" + paper["doi"]


def citation(paper):
    return f'{text(paper["venue"])} <span class="middle-dot">·</span> {text(paper["citation"])}'


def research_section(language):
    h = LABELS[language]
    items = "".join(
        f'''
        <li class="research-item">
          <h3>{local(topic["title"], language)}</h3>
          <p>{local(topic["description"], language)}</p>
        </li>'''
        for topic in DATA["research"]
    )
    return f'''
    <section class="shell section research-section" id="research" aria-labelledby="research-title">
      <div class="section-heading"><h2 id="research-title">{h["research"]}</h2></div>
      <ul class="research-list" role="list">{items}</ul>
    </section>'''


def selected_papers(language, person):
    h = LABELS[language]
    other = "en" if language == "zh" else "zh"
    cards = []
    for paper in DATA["publications"]:
        if "summary" not in paper:
            continue
        paper_url = doi_link(paper)
        cards.append(f'''
        <article class="feature-card">
          <div class="feature-top">
            <p class="journal" lang="en">{text(paper["venue"])}</p>
            <span class="feature-year">{text(paper["year"])}</span>
          </div>
          <p class="paper-role">{h[paper["role"]]}</p>
          <h3><a href="{text(paper_url)}" target="_blank" rel="noopener noreferrer">{local(paper["title"], language)}</a></h3>
          <p class="paper-translation" lang="{other}">{local(paper["title"], other)}</p>
          <p class="feature-summary">{local(paper["summary"], language)}</p>
          <p class="author-line" lang="en">{shown_names(paper["authors"], person)}</p>
          <div class="feature-links">
            {link(h["doi"], paper_url, external=True, icon="↗")}
            <span class="feature-cite" lang="en">{text(paper["citation"])}</span>
          </div>
        </article>''')
    return f'''
    <section class="shell section selected-section" id="selected" aria-labelledby="selected-title">
      <div class="section-heading"><h2 id="selected-title">{h["selected"]}</h2></div>
      <div class="feature-grid">{"".join(cards)}</div>
    </section>'''


def benchmark_section(language):
    h = LABELS[language]
    project = DATA["benchmark"]
    return f'''
    <aside class="shell benchmark-section" aria-labelledby="benchmark-title">
      <div class="benchmark">
        <div>
          <p class="eyebrow">{h["benchmark"]}</p>
          <h2 id="benchmark-title">{local(project["title"], language)}</h2>
          <p class="benchmark-body">{local(project["description"], language)}</p>
        </div>
        {link(h["view_benchmark"], project["url"], css="button button-light", external=True, icon="↗")}
      </div>
    </aside>'''


def all_papers(language, person):
    h = LABELS[language]
    topics = DATA["publication_topics"]
    rows = []
    for paper in sorted(DATA["publications"], key=lambda p: p["year"], reverse=True):
        record_name = h["proceedings"] if paper["type"] == "conference" else h["doi"]
        search_text = " ".join((*paper["title"].values(), *paper["authors"], paper["venue"], paper["doi"]))
        english_title = ""
        if language == "zh":
            english_title = f'\n            <p class="list-translation" lang="en">{local(paper["title"], "en")}</p>'
        rows.append(f'''
        <li class="publication" data-topic="{text(paper["topic"])}" data-search="{text(search_text)}">
          <span class="publication-year">{text(paper["year"])}</span>
          <div class="publication-main">
            <h3>{local(paper["title"], language)}</h3>{english_title}
            <p class="author-line" lang="en">{shown_names(paper["authors"], person)}</p>
            <p class="record-details"><span lang="en">{citation(paper)}</span> <span class="middle-dot">·</span> {h[paper["role"]]}</p>
          </div>
          {link(record_name, doi_link(paper), css="text-link record-link", external=True, icon="↗")}
        </li>''')
    filters = "".join(
        f'<button type="button" data-filter="{text(key)}" aria-pressed="false">{local(title, language)}</button>'
        for key, title in topics.items()
    )
    return f'''
    <section class="shell section publications-section" id="publications" aria-labelledby="publications-title">
      <div class="section-heading"><h2 id="publications-title">{h["publications"]}</h2></div>
      <div class="publication-controls" data-controls hidden>
        <div class="topic-filters" role="group" aria-label="{h["filter"]}">
          <button type="button" data-filter="all" aria-pressed="true">{h["all"]}</button>{filters}
        </div>
        <label class="search">
          <span class="search-icon" aria-hidden="true"></span>
          <span class="sr-only">{h["keywords"]}</span>
          <input type="search" placeholder="{h["keywords"]}" data-search-input>
        </label>
      </div>
      <p class="sr-only" role="status" data-results data-format="{text(h["results"])}"></p>
      <ul class="publication-list" role="list">{"".join(rows)}</ul>
      <p class="no-results" data-empty hidden>{h["no_results"]}</p>
    </section>'''


def patent_section(language, person):
    h = LABELS[language]
    if not DATA["patents"]:
        return ""
    patents = []
    for patent in sorted(DATA["patents"], key=lambda p: p["date"], reverse=True):
        patents.append(f'''
        <li class="record-card">
          <p class="record-id">{text(patent["number"])} <span class="middle-dot">·</span> {h[patent["status"]]}</p>
          <h3>{local(patent["title"], language)}</h3>
          <p class="record-details">{local(patent["applicant"], language)} <span class="middle-dot">·</span>
            <time datetime="{text(patent["date"])}">{month(patent["date"], language, with_day=True)}</time>
          </p>
          <p class="author-line">{h["inventors"]} <span class="middle-dot">·</span> {shown_names(patent["inventors"][language], person)}</p>
          {link(h["patent_record"], patent["url"], external=True, icon="↗")}
        </li>''')
    return f'''
    <section class="shell section patents-section" id="patents" aria-labelledby="patents-title">
      <div class="section-heading"><h2 id="patents-title">{h["patents"]}</h2></div>
      <ul class="patent-grid" role="list">{"".join(patents)}</ul>
    </section>'''


def event_section(language):
    h = LABELS[language]
    if not DATA["events"]:
        return ""
    papers = {paper["id"]: paper for paper in DATA["publications"]}
    events = []
    for event in sorted(DATA["events"], key=lambda e: e["date"], reverse=True):
        subject = papers[event["paper"]]["title"] if "paper" in event else event["description"]
        events.append(f'''
        <li class="event">
          <div class="event-meta">
            <time datetime="{text(event["date"])}">{month(event["date"], language)}</time>
            <span>{local(event["location"], language)}</span>
          </div>
          <div class="event-content">
            <h3>{local(event["title"], language)}</h3>
            <p><span class="event-role">{local(event["role"], language)}</span> {local(subject, language)}</p>
          </div>
          {link(event["link_label"][language], event["url"], css="text-link record-link", external=True, icon="↗")}
        </li>''')
    return f'''
    <section class="shell section events-section" id="events" aria-labelledby="events-title">
      <div class="section-heading"><h2 id="events-title">{h["events"]}</h2></div>
      <ul class="event-list" role="list">{"".join(events)}</ul>
    </section>'''


def render(language):
    h = LABELS[language]
    english = language == "en"
    person = DATA["person"]
    title = local(person["page_title"], language)
    page_path = "en/" if english else ""
    relative = "../" if english else "./"
    canonical = urljoin(DATA["site_url"], page_path)
    english_url = urljoin(DATA["site_url"], "en/")
    other = "zh" if english else "en"
    nav_items = ["research", "publications"]
    nav_items += [key for key in ("patents", "events") if DATA[key]]
    nav = "".join(f'<a href="#{key}">{h[key]}</a>' for key in nav_items)
    hero = DATA["hero"]
    profile_link = link("GitHub", person["github"], css="button button-outline", external=True, icon="↗")
    sections = "".join((
        research_section(language),
        selected_papers(language, person),
        benchmark_section(language),
        all_papers(language, person),
        patent_section(language, person),
        event_section(language),
    ))
    structured = json.dumps({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": person["name"]["en"],
        "alternateName": person["name"]["zh"],
        "url": DATA["site_url"],
        "sameAs": [person["github"]],
        "affiliation": {
            "@type": "Organization",
            "name": "Huazhong University of Science and Technology",
            "url": "https://www.hust.edu.cn/",
        },
    }, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!doctype html>
<html lang="{"en" if english else "zh-CN"}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{local(person["description"], language)}">
  <meta name="theme-color" content="#f8f7f2">
  <link rel="canonical" href="{text(canonical)}">
  <link rel="alternate" hreflang="zh-CN" href="{text(DATA["site_url"])}">
  <link rel="alternate" hreflang="en" href="{text(english_url)}">
  <link rel="alternate" hreflang="x-default" href="{text(DATA["site_url"])}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{local(person["description"], language)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{text(canonical)}">
  <meta property="og:image" content="{text(urljoin(DATA["site_url"], hero["file"]))}">
  <meta property="og:image:alt" content="{local(hero["alt"], language)}">
  <link rel="icon" href="{relative}assets/favicon.png" type="image/png">
  <link rel="stylesheet" href="{relative}assets/site.css">
  <script src="{relative}assets/site.js" defer></script>
  <script type="application/ld+json">{structured}</script>
</head>
<body id="top">
  <a href="#main" class="skip-link">{h["skip"]}</a>
  <header class="site-header">
    <div class="shell masthead">
      <a class="brand" href="#top"><span class="brand-mark" aria-hidden="true">JS</span>{local(person["name"], language)}</a>
      <nav class="primary-nav" aria-label="{h["navigation"]}">{nav}</nav>
      <div class="languages" role="group" aria-label="{h["language"]}">
        <a href="{relative}" lang="zh-CN" hreflang="zh-CN"{" aria-current='page'" if not english else ""}>中文</a>
        <a href="{relative}en/" lang="en" hreflang="en"{" aria-current='page'" if english else ""}>EN</a>
      </div>
    </div>
  </header>
  <main id="main">
    <section class="shell hero" aria-labelledby="hero-title">
      <div class="hero-content">
        <p class="eyebrow hero-field">{local(person["field"], language)}</p>
        <h1 id="hero-title">{local(person["name"], language)}</h1>
        <p class="alternate-name" lang="{other}">{local(person["name"], other)}</p>
        <p class="affiliation">{local(person["affiliation"], language)}</p>
        <p class="hero-intro">{local(person["intro"], language)}</p>
        <div class="hero-links">
          {link(h["selected"], "#selected", css="button button-primary", icon="↓")}
          {profile_link}
        </div>
      </div>
      <figure class="hero-figure">
        <img src="{relative}{text(hero["file"])}" alt="{local(hero["alt"], language)}" width="{hero["width"]}"
          height="{hero["height"]}" fetchpriority="high">
        <figcaption>{local(hero["caption"], language)}</figcaption>
      </figure>
    </section>{sections}
  </main>
  <footer class="site-footer">
    <div class="shell footer-content">
      <div>
        <p class="footer-name">{local(person["name"], language)} <span lang="{other}">{local(person["name"], other)}</span></p>
        <p class="footer-date">{h["updated"]} <time datetime="{text(DATA["updated"])}">{month(DATA["updated"], language, with_day=True)}</time></p>
      </div>
      <div class="footer-links">
        {link("GitHub", person["github"], external=True, icon="↗")}
        {link(h["top"], "#top", icon="↑")}
      </div>
    </div>
  </footer>
</body>
</html>
'''


def main():
    for language, folder in (("zh", OUTPUT), ("en", OUTPUT / "en")):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(render(language), encoding="utf-8", newline="\n")
    urls = (DATA["site_url"], urljoin(DATA["site_url"], "en/"))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{text(url)}</loc></url>\n" for url in urls) + "</urlset>\n"
    (OUTPUT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    print(f'Built both languages with {len(DATA["publications"])} publications, {len(DATA["patents"])} patent records and {len(DATA["events"])} conference entries.')


if __name__ == "__main__":
    main()
