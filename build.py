"""Build the Chinese and English GitHub Pages site using the Python standard library."""

import json
from datetime import date
from hashlib import sha256
from html import escape
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "docs"
DATA = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
ASSET_VERSIONS = {
    # Text-mode reads keep the cache key stable across checkout line endings.
    name: sha256((OUTPUT / "assets" / name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:12]
    for name in ("site.css", "site.js")
}

LABELS = {
    "zh": {
        "skip": "跳到正文",
        "navigation": "主要栏目",
        "language": "语言",
        "about": "关于我",
        "research": "研究方向",
        "scenes": "加工场景",
        "view_scenes": "查看加工场景",
        "selected": "代表论文",
        "publications": "论文",
        "patents": "专利",
        "events": "学术会议",
        "benchmark": "开放基准",
        "view_benchmark": "查看基准仓库",
        "doi": "出版方原文",
        "details": "阅读详情",
        "back_to_papers": "返回论文列表",
        "overview": "摘要概述",
        "contributions": "主要贡献",
        "citation": "推荐引用",
        "copy": "复制引用",
        "copied": "引用已复制",
        "copy_error": "可选中引用文本手动复制。",
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
        "about": "About me",
        "research": "Research",
        "scenes": "Machining scenes",
        "view_scenes": "View machining scenes",
        "selected": "Selected papers",
        "publications": "Publications",
        "patents": "Patents",
        "events": "Conferences",
        "benchmark": "Open benchmark",
        "view_benchmark": "Explore the benchmark",
        "doi": "Publisher’s version",
        "details": "Read more",
        "back_to_papers": "Back to publications",
        "overview": "Abstract summary",
        "contributions": "Key contributions",
        "citation": "Recommended citation",
        "copy": "Copy citation",
        "copied": "Citation copied",
        "copy_error": "Select the citation text to copy it manually.",
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


def paper_path(paper):
    return f'papers/{paper["id"]}/'


def citation(paper):
    return f'{text(paper["venue"])} <span class="middle-dot">·</span> {text(paper["citation"])}'


def scene_section(language, asset_prefix):
    h = LABELS[language]
    scenes = DATA["scenes"]
    if not scenes:
        return ""
    figures = "".join(
        f'''
        <figure class="scene">
          <img src="{asset_prefix}{text(scene["file"])}" alt="{local(scene["alt"], language)}"
            width="{scene["width"]}" height="{scene["height"]}" loading="lazy">
          <figcaption>
            <h3>{local(scene["title"], language)}</h3>
            <p>{local(scene["caption"], language)}</p>
          </figcaption>
        </figure>'''
        for scene in scenes
    )
    return f'''
    <section class="shell section scenes-section" id="scenes" aria-labelledby="scenes-title">
      <div class="section-heading"><h2 id="scenes-title">{h["scenes"]}</h2></div>
      <div class="scene-grid">{"".join(figures)}</div>
    </section>'''


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
        path = paper_path(paper)
        cards.append(f'''
        <article class="feature-card">
          <div class="feature-top">
            <p class="journal" lang="en">{text(paper["venue"])}</p>
            <span class="feature-year">{text(paper["year"])}</span>
          </div>
          <p class="paper-role">{h[paper["role"]]}</p>
          <h3><a href="{text(path)}">{local(paper["title"], language)}</a></h3>
          <p class="paper-translation" lang="{other}">{local(paper["title"], other)}</p>
          <p class="feature-summary">{local(paper["summary"], language)}</p>
          <p class="author-line" lang="en">{shown_names(paper["authors"], person)}</p>
          <div class="feature-links">
            <div class="publication-links">
              {link(h["details"], path, icon="→")}
              {link("DOI", doi_link(paper), css="text-link doi-shortcut", external=True, icon="↗")}
            </div>
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
        path = paper_path(paper)
        search_text = " ".join((*paper["title"].values(), *paper["authors"], paper["venue"], paper["doi"]))
        english_title = ""
        if language == "zh":
            english_title = f'\n            <p class="list-translation" lang="en">{local(paper["title"], "en")}</p>'
        rows.append(f'''
        <li class="publication" data-topic="{text(paper["topic"])}" data-search="{text(search_text)}">
          <span class="publication-year">{text(paper["year"])}</span>
          <div class="publication-main">
            <h3><a href="{text(path)}">{local(paper["title"], language)}</a></h3>{english_title}
            <p class="author-line" lang="en">{shown_names(paper["authors"], person)}</p>
            <p class="record-details"><span lang="en">{citation(paper)}</span> <span class="middle-dot">·</span> {h[paper["role"]]}</p>
          </div>
          <div class="publication-links record-link">
            {link(h["details"], path, icon="→")}
            {link("DOI", doi_link(paper), css="text-link doi-shortcut", external=True, icon="↗")}
          </div>
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


def about_section(language, person, asset_prefix):
    h = LABELS[language]
    other = "en" if language == "zh" else "zh"
    portrait = DATA["portrait"]
    paragraphs = "".join(f'\n          <p>{local(part, language)}</p>' for part in person["about"])
    actions = [link(h["selected"], "#selected", css="button button-primary", icon="↓")]
    if DATA["scenes"]:
        actions.append(link(h["view_scenes"], "#scenes", css="button button-outline", icon="↓"))
    return f'''
    <section class="shell about" id="about" aria-labelledby="about-title">
      <div class="profile">
        <img class="profile-photo" src="{asset_prefix}{text(portrait["file"])}" alt="{local(portrait["alt"], language)}"
          width="{portrait["width"]}" height="{portrait["height"]}" fetchpriority="high">
        <div class="profile-info">
          <p class="profile-name">{local(person["name"], language)}</p>
          <p class="profile-alternate" lang="{other}">{local(person["name"], other)}</p>
          <p class="affiliation">{local(person["affiliation"], language)}</p>
          {link("GitHub", person["github"], external=True, icon="↗")}
        </div>
      </div>
      <div class="about-content">
        <p class="eyebrow">{local(person["field"], language)}</p>
        <h1 id="about-title">{h["about"]}</h1>
        <div class="about-text">{paragraphs}
        </div>
        <div class="about-links">{"".join(actions)}</div>
      </div>
    </section>'''


def recommended_citation(paper):
    names = []
    for name in paper["authors"]:
        given, _, surname = name.rpartition(" ")
        initials = " ".join(f"{part[0]}." for part in given.split())
        names.append(f"{surname}, {initials}" if initials else surname)
    authors = ", ".join(names)
    if len(names) > 1:
        authors = ", ".join(names[:-1]) + ", & " + names[-1]
    title = paper["title"]["en"].rstrip(".")
    return (f'{authors} ({paper["year"]}). {title}. {paper["venue"]}, {paper["citation"]}. '
            f'{doi_link(paper)}')


def render_paper(language, paper, detail):
    person = DATA["person"]
    h = LABELS[language]
    other = "en" if language == "zh" else "zh"
    headings = (local(paper["title"], language), local(paper["title"], other))
    contributions = "".join(f'\n              <li>{local(item, language)}</li>' for item in detail["contributions"])
    reference = text(recommended_citation(paper))
    actions = [link(h["doi"], doi_link(paper), css="button button-primary", external=True, icon="↗")]
    if paper["id"] in ("potential-network", "prime"):
        actions.append(link(h["view_benchmark"], DATA["benchmark"]["url"],
                            css="button button-outline", external=True, icon="↗"))
    content = f'''
    <article class="shell paper-page" aria-labelledby="paper-title">
      <a class="text-link paper-back" href="../../#publications">{arrow("←")}{h["back_to_papers"]}</a>
      <header class="paper-header">
        <p class="eyebrow"><span lang="en">{text(paper["venue"])}</span>
          <span class="middle-dot">·</span> {text(paper["year"])} <span class="middle-dot">·</span> {h[paper["role"]]}
        </p>
        <h1 id="paper-title">{headings[0]}</h1>
        <p class="paper-subtitle" lang="{other}">{headings[1]}</p>
        <p class="author-line" lang="en">{shown_names(paper["authors"], person)}</p>
        <div class="paper-actions">{"".join(actions)}</div>
      </header>
      <div class="paper-layout">
        <div class="paper-reading">
          <section aria-labelledby="paper-overview">
            <h2 id="paper-overview">{h["overview"]}</h2>
            <p>{local(detail["overview"], language)}</p>
          </section>
          <section aria-labelledby="paper-contributions">
            <h2 id="paper-contributions">{h["contributions"]}</h2>
            <ul class="contribution-list">{contributions}
            </ul>
          </section>
        </div>
        <aside class="citation-card" aria-labelledby="paper-citation">
          <h2 id="paper-citation">{h["citation"]}</h2>
          <p lang="en" data-citation>{reference}</p>
          <button class="button button-outline" type="button" data-copy-citation
            data-copied="{text(h["copied"])}" data-copy-error="{text(h["copy_error"])}" hidden>{h["copy"]}</button>
          <p class="copy-status" role="status" data-copy-status></p>
        </aside>
      </div>
    </article>'''
    metadata = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": paper["title"]["en"],
        "author": [{"@type": "Person", "name": name} for name in paper["authors"]],
        "datePublished": str(paper["year"]),
        "sameAs": doi_link(paper),
        "isPartOf": {"name": paper["venue"]},
    }
    title = f'{paper["title"][language]} | {person["name"][language]}'
    return render_document(language, content, title=title, description=detail["overview"][language],
                           metadata=metadata, path=paper_path(paper))


def render_document(language, content, *, title, description, metadata, path=""):
    h = LABELS[language]
    english = language == "en"
    person = DATA["person"]
    prefix = "en/" if english else ""
    page_path = prefix + path
    relative = "../" * page_path.count("/") if page_path else "./"
    canonical = urljoin(DATA["site_url"], page_path)
    zh_url = urljoin(DATA["site_url"], path)
    english_url = urljoin(DATA["site_url"], "en/" + path)
    other = "zh" if english else "en"
    nav_items = ["about", "research", "publications"]
    nav_items += [key for key in ("patents", "events") if DATA[key]]
    home = relative + prefix if path else ""
    nav = "".join(f'<a href="{home}#{key}">{h[key]}</a>' for key in nav_items)
    portrait = DATA["portrait"]
    image_meta = ""
    if not path:
        image_meta = f'''
  <meta property="og:image" content="{text(urljoin(DATA["site_url"], portrait["file"]))}">
  <meta property="og:image:alt" content="{local(portrait["alt"], language)}">'''
    structured = json.dumps(metadata, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!doctype html>
<html lang="{"en" if english else "zh-CN"}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{text(title)}</title>
  <meta name="description" content="{text(description)}">
  <meta name="theme-color" content="#f8f7f2">
  <link rel="canonical" href="{text(canonical)}">
  <link rel="alternate" hreflang="zh-CN" href="{text(zh_url)}">
  <link rel="alternate" hreflang="en" href="{text(english_url)}">
  <link rel="alternate" hreflang="x-default" href="{text(zh_url)}">
  <meta property="og:title" content="{text(title)}">
  <meta property="og:description" content="{text(description)}">
  <meta property="og:type" content="{"article" if path else "website"}">
  <meta property="og:url" content="{text(canonical)}">{image_meta}
  <link rel="icon" href="{relative}assets/favicon.png" type="image/png">
  <link rel="stylesheet" href="{relative}assets/site.css?v={ASSET_VERSIONS["site.css"]}">
  <script src="{relative}assets/site.js?v={ASSET_VERSIONS["site.js"]}" defer></script>
  <script type="application/ld+json">{structured}</script>
</head>
<body id="top">
  <a href="#main" class="skip-link">{h["skip"]}</a>
  <header class="site-header">
    <div class="shell masthead">
      <a class="brand" href="{home}#top"><span class="brand-mark" aria-hidden="true">JS</span>{local(person["name"], language)}</a>
      <nav class="primary-nav" aria-label="{h["navigation"]}">{nav}</nav>
      <div class="languages" role="group" aria-label="{h["language"]}">
        <a href="{relative}{path}" lang="zh-CN" hreflang="zh-CN"{" aria-current='page'" if not english else ""}>中文</a>
        <a href="{relative}en/{path}" lang="en" hreflang="en"{" aria-current='page'" if english else ""}>EN</a>
      </div>
    </div>
  </header>
  <main id="main" tabindex="-1">{content}
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


def render_home(language):
    person = DATA["person"]
    asset_prefix = "../" if language == "en" else "./"
    metadata = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": person["name"]["en"],
        "alternateName": person["name"]["zh"],
        "url": DATA["site_url"],
        "image": urljoin(DATA["site_url"], DATA["portrait"]["file"]),
        "sameAs": [person["github"]],
        "affiliation": {
            "@type": "Organization",
            "name": "Huazhong University of Science and Technology",
            "url": "https://www.hust.edu.cn/",
        },
    }
    content = "".join((
        about_section(language, person, asset_prefix),
        research_section(language),
        scene_section(language, asset_prefix),
        selected_papers(language, person),
        benchmark_section(language),
        all_papers(language, person),
        patent_section(language, person),
        event_section(language),
    ))
    return render_document(language, content, title=person["page_title"][language],
                           description=person["description"][language], metadata=metadata)


def write_page(path, content):
    folder = OUTPUT / path
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(content, encoding="utf-8", newline="\n")


def main():
    papers = DATA["publications"]
    details = json.loads((ROOT / "content" / "paper-details.json").read_text(encoding="utf-8"))
    paper_ids = {paper["id"] for paper in papers}
    if len(paper_ids) != len(papers) or set(details) != paper_ids:
        raise ValueError("Use unique publication IDs and one matching paper-details entry per publication.")

    paths = []
    for language, prefix in (("zh", ""), ("en", "en/")):
        write_page(prefix, render_home(language))
        paths.append(prefix)
        for paper in papers:
            path = prefix + paper_path(paper)
            write_page(path, render_paper(language, paper, details[paper["id"]]))
            paths.append(path)

    urls = [urljoin(DATA["site_url"], path) for path in paths]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{text(url)}</loc></url>\n" for url in urls) + "</urlset>\n"
    (OUTPUT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    print(f'Built {len(paths)} pages across both languages, including {len(papers)} publication profiles per language.')


if __name__ == "__main__":
    main()
