"""Collects the BBC RSS dataset used for the Task 2 clustering experiment."""

import csv
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import feedparser
import requests
from bs4 import BeautifulSoup

from config import PROJECT_DIR

# RSS feeds used for the three coursework categories.

FEEDS = {
    "Economics": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.bbci.co.uk/news/business/economy/rss.xml",
    ],
    "Entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    ],
    "Politics": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://feeds.bbci.co.uk/news/uk_politics/rss.xml",
    ],
}

# Business feeds are broad, so these terms keep the Economics sample on-topic.

ECONOMICS_KEYWORDS = {
    "inflation", "economy", "economic", "gdp", "monetary", "fiscal",
    "interest rate", "unemployment", "recession", "trade", "tariff",
    "tax", "growth", "central bank", "imf", "world bank", "employment",
    "deficit", "surplus", "debt", "bond", "yield", "exchange rate",
    "market", "stock", "ftse", "dow", "s&p", "wage", "consumer price",
    "cost of living", "housing market", "treasury", "budget", "financial",
    "banking", "bank of england", "federal reserve", "ecb", "forex",
    "commodity", "oil price", "energy price", "export", "import",
    "manufacturing", "retail", "spending", "borrowing", "mortgage",
    "pension", "savings",
}

MIN_TEXT_LENGTH = 50
FETCH_DELAY = 1.0  # Pause between full-article requests.
OUTPUT_DIR = PROJECT_DIR / "data" / "clustering"
CSV_PATH = OUTPUT_DIR / "documents.csv"
METADATA_PATH = OUTPUT_DIR / "dataset_metadata.json"

# Small cleaning and validation helpers.


def _clean_html(raw_html: str) -> str:
    """Strip HTML tags from an RSS description field."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _normalize_title(title: str) -> str:
    """Produce a canonical title for deduplication."""
    text = unicodedata.normalize("NFKD", title)
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _canonical_url(url: str) -> str:
    """Strip query params and trailing slashes for dedup."""
    url = url.split("?")[0].split("#")[0]
    return url.rstrip("/")


def _is_meaningful(text: str) -> bool:
    """Reject text that is too short or non-meaningful."""
    if len(text) < MIN_TEXT_LENGTH:
        return False
    # Ignore entries that contain very little real text.
    alpha_count = sum(1 for ch in text if ch.isalpha())
    if alpha_count < MIN_TEXT_LENGTH * 0.4:
        return False
    return True


def _is_economics_relevant(text: str) -> bool:
    """Check if a Business-feed entry genuinely concerns economic themes."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in ECONOMICS_KEYWORDS)


def _parse_published(entry) -> str:
    """Extract a published date string from an RSS entry."""
    published = entry.get("published") or entry.get("updated") or ""
    return published


def _fetch_article_body(url: str) -> str | None:
    """Attempt to fetch the full article text from a BBC page.

    Returns the article body text, or None if it cannot be extracted.
    """
    if not url or "bbc." not in url.lower():
        return None
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Softwarica-IR-Coursework/1.0"},
            timeout=12,
        )
        resp.raise_for_status()
    except Exception:
        return None

    if "text/html" not in resp.headers.get("Content-Type", "").lower():
        return None

    soup = BeautifulSoup(resp.content, "html.parser")
    article = soup.find("article") or soup.find("main")
    if article is None:
        return None

    paragraphs = []
    seen = set()
    for p in article.find_all("p"):
        text = p.get_text(" ", strip=True)
        key = text.casefold()
        if len(text) < 20 or key in seen:
            continue
        seen.add(key)
        paragraphs.append(text)

    body = " ".join(paragraphs).strip()
    return body if len(body) >= MIN_TEXT_LENGTH else None


# Main collection pipeline.


def collect_dataset():
    """Run the full RSS → CSV pipeline and return statistics."""
    collection_time = datetime.now(timezone.utc).isoformat()

    stats = {
        "rss_entries_fetched": {},
        "rejected_short": 0,
        "rejected_non_meaningful": 0,
        "rejected_economics_filter": 0,
        "duplicate_url_removals": 0,
        "duplicate_title_removals": 0,
    }

    raw_entries = []

    # Read every configured RSS feed first.
    for category, feed_urls in FEEDS.items():
        category_count = 0
        for feed_url in feed_urls:
            print(f"  Fetching {feed_url} ...")
            parsed = feedparser.parse(feed_url)
            entries = parsed.get("entries", [])
            category_count += len(entries)

            for entry in entries:
                title = (entry.get("title") or "").strip()
                description = _clean_html(
                    entry.get("summary") or entry.get("description") or ""
                )
                link = (entry.get("link") or "").strip()
                published = _parse_published(entry)

                raw_entries.append(
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "published": published,
                        "feed_category": category,
                    }
                )

        stats["rss_entries_fetched"][category] = category_count

    print(f"\n  Total RSS entries fetched: {len(raw_entries)}")

    # Filter broad Business entries before downloading full article pages.
    relevance_filtered = []
    for entry in raw_entries:
        if entry["feed_category"] == "Economics":
            relevance_text = f"{entry['title']} {entry['description']}"
            if not _is_economics_relevant(relevance_text):
                stats["rejected_economics_filter"] += 1
                continue
        relevance_filtered.append(entry)

    # Prefer the full article text; use the RSS summary when it is unavailable.
    stats["full_article_fetched"] = 0
    stats["full_article_failed"] = 0
    candidates = []
    for i, entry in enumerate(relevance_filtered):
        # Fetch the full article when a link is available.
        article_body = None
        if entry["link"]:
            if i > 0:
                time.sleep(FETCH_DELAY)
            print(f"    [{i+1}/{len(relevance_filtered)}] Fetching {entry['link'][:80]}...")
            article_body = _fetch_article_body(entry["link"])

        if article_body:
            text = f"{entry['title']} {article_body}"
            stats["full_article_fetched"] += 1
        else:
            # The RSS summary is enough to keep a usable document if the page cannot be read.
            text = entry["title"]
            if entry["description"]:
                text = f"{entry['title']} {entry['description']}"
            stats["full_article_failed"] += 1

        if len(text.strip()) < MIN_TEXT_LENGTH:
            stats["rejected_short"] += 1
            continue

        if not _is_meaningful(text):
            stats["rejected_non_meaningful"] += 1
            continue

        entry["text"] = text.strip()
        candidates.append(entry)

    # Remove duplicate article URLs.
    seen_urls = set()
    url_deduped = []
    for entry in candidates:
        canonical = _canonical_url(entry["link"])
        if canonical and canonical in seen_urls:
            stats["duplicate_url_removals"] += 1
            continue
        if canonical:
            seen_urls.add(canonical)
        url_deduped.append(entry)

    # Remove duplicate titles that may appear in more than one feed.
    seen_titles = set()
    title_deduped = []
    for entry in url_deduped:
        norm_title = _normalize_title(entry["title"])
        if norm_title and norm_title in seen_titles:
            stats["duplicate_title_removals"] += 1
            continue
        if norm_title:
            seen_titles.add(norm_title)
        title_deduped.append(entry)

    # The remaining entries are clean enough to build the final corpus.
    filtered = title_deduped

    # Convert the entries into the CSV rows used by the clustering pipeline.
    documents = []
    for idx, entry in enumerate(filtered, start=1):
        documents.append(
            {
                "id": idx,
                "text": entry["text"],
                "category": entry["feed_category"],
                "source": "BBC News",
                "url": entry["link"],
                "published": entry["published"],
                "title": entry["title"],
            }
        )

    # Record the final category balance.
    category_counts = {}
    for doc in documents:
        category_counts[doc["category"]] = (
            category_counts.get(doc["category"], 0) + 1
        )

    # Record basic document-length statistics for evidence.
    doc_lengths = [len(doc["text"]) for doc in documents]
    avg_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0
    min_length = min(doc_lengths) if doc_lengths else 0
    max_length = max(doc_lengths) if doc_lengths else 0

    # The coursework requires at least 100 documents in total.
    total = len(documents)
    required_categories = {"Economics", "Entertainment", "Politics"}
    present_categories = set(category_counts.keys())
    missing_categories = required_categories - present_categories

    print("\n" + "=" * 60)
    print("DATASET COLLECTION STATISTICS")
    print("=" * 60)
    for cat, count in sorted(stats["rss_entries_fetched"].items()):
        print(f"  RSS entries fetched ({cat}):       {count}")
    print(f"  Full articles fetched:               {stats['full_article_fetched']}")
    print(f"  Full article fetch failed (fallback):{stats['full_article_failed']}")
    print(f"  Rejected as too short:              {stats['rejected_short']}")
    print(f"  Rejected as non-meaningful:          {stats['rejected_non_meaningful']}")
    print(f"  Rejected by Economics filter:        {stats['rejected_economics_filter']}")
    print(f"  Duplicate URL removals:              {stats['duplicate_url_removals']}")
    print(f"  Duplicate title removals:            {stats['duplicate_title_removals']}")
    print("-" * 60)
    for cat in sorted(category_counts.keys()):
        print(f"  Final {cat} count:           {category_counts[cat]}")
    print(f"  Final total:                         {total}")
    print(f"  Unique URLs:                         {len({_canonical_url(doc['url']) for doc in documents if doc['url']})}")
    print(f"  Average document length (chars):     {avg_length:.0f}")
    print(f"  Minimum document length (chars):     {min_length}")
    print(f"  Maximum document length (chars):     {max_length}")
    print("=" * 60)

    if missing_categories:
        raise ValueError(
            f"FAILED: Missing required categories: {sorted(missing_categories)}. "
            f"Cannot produce a valid dataset."
        )

    if total < 100:
        raise ValueError(
            f"FAILED: Only {total} valid documents after filtering and "
            f"deduplication. At least 100 are required. "
            f"Do not relax quality rules — investigate feed availability."
        )

    # Save the corpus used by training.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "text", "category", "source", "url", "published", "title"],
        )
        writer.writeheader()
        writer.writerows(documents)

    print(f"\n  Saved {total} documents to {CSV_PATH}")

    # Save collection metadata so the report can reproduce the dataset evidence.
    feed_urls_flat = []
    for cat, urls in FEEDS.items():
        for url in urls:
            feed_urls_flat.append({"category": cat, "url": url})

    metadata = {
        "collected_at": collection_time,
        "feeds": feed_urls_flat,
        "sources": sorted({f"{cat} RSS" for cat in FEEDS}),
        "total_documents": total,
        "category_counts": dict(sorted(category_counts.items())),
        "duplicates_removed": {
            "url": stats["duplicate_url_removals"],
            "title": stats["duplicate_title_removals"],
        },
        "short_entries_removed": stats["rejected_short"],
        "non_meaningful_entries_removed": stats["rejected_non_meaningful"],
        "economics_filter_rejections": stats["rejected_economics_filter"],
        "rss_entries_fetched": stats["rss_entries_fetched"],
        "full_article_fetched": stats["full_article_fetched"],
        "full_article_failed": stats["full_article_failed"],
        "avg_document_length": round(avg_length),
        "min_document_length": min_length,
        "max_document_length": max_length,
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"  Saved metadata to {METADATA_PATH}")

    return documents, metadata


# Allow the script to be run directly from the command line.

if __name__ == "__main__":
    print("Collecting Task 2 clustering dataset from BBC News RSS feeds...\n")
    collect_dataset()
    print("\nDone.")
