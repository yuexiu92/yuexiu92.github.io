#!/usr/bin/env python3
"""Refresh only citation data from the configured public Google Scholar profile."""

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sys
import time
import unicodedata
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup


BADGE = re.compile(
    r" \[!\[Citations: \d+\]\(https://img\.shields\.io/badge/"
    r"Citations-\d+-ffc107\?style=flat\)\]"
    r"\(https://scholar\.google\.com/scholar\?[^)]+\)"
)
PUBLICATION = re.compile(r"^1\. `[^`]+` \[([^]]+)\]\(")


@dataclass(frozen=True)
class Paper:
    title: str
    citations: int
    clusters: tuple
    identity: str


@dataclass(frozen=True)
class Page:
    total: int
    papers: tuple
    has_more: bool


def scalar(config, key):
    match = re.search(r"^  " + key + r"\s*:\s*(.+?)\s*$", config, re.M)
    if not match:
        raise ValueError(f"Missing author.{key} in _config.yml")
    return match[1].strip("\"'")


def normalize(title):
    return "".join(c for c in unicodedata.normalize("NFKC", title).casefold() if c.isalnum())


def cluster_ids(url):
    values = parse_qs(urlparse(url).query).get("cites", [""])[0]
    return tuple(value for value in values.split(",") if value)


def number(text):
    text = text.strip().replace(",", "").rstrip("*")
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError(f"Invalid citation count: {text!r}")
    return int(text)


def parse_page(html, user, name):
    soup = BeautifulSoup(html, "html.parser")
    canonical = soup.select_one('link[rel="canonical"]')
    profile = soup.select_one("#gsc_prf_in")
    stats = soup.select(".gsc_rsb_std")
    more = soup.select_one("#gsc_bpf_more")
    if (not canonical or parse_qs(urlparse(canonical.get("href", "")).query).get("user") != [user]
            or not profile or normalize(profile.get_text()) != normalize(name)
            or not stats or more is None):
        raise ValueError("Incomplete or blocked Scholar response, or profile identity mismatch")
    total = number(stats[0].get_text())
    if total <= 0:
        raise ValueError("Refusing an empty citation snapshot")
    papers = []
    for row in soup.select("tr.gsc_a_tr"):
        title = row.select_one(".gsc_a_at")
        cited = row.select_one(".gsc_a_ac")
        if not title or cited is None or not title.get_text(strip=True):
            raise ValueError("Incomplete Scholar publication row")
        identity = parse_qs(urlparse(title.get("href", "")).query).get("citation_for_view", [""])[0]
        if not identity.startswith(user + ":"):
            raise ValueError("Missing or unexpected Scholar publication identity")
        count_text = cited.get_text(strip=True)
        count = number(count_text) if count_text else 0
        clusters = cluster_ids(cited.get("href", ""))
        if count and (not clusters or any(not value.isdigit() for value in clusters)):
            raise ValueError("Cited publication is missing a valid cited-by link")
        papers.append(Paper(title.get_text(strip=True), count, clusters, identity))
    if not papers:
        raise ValueError("Scholar returned no publication rows")
    return Page(total, tuple(papers), not more.has_attr("disabled"))


def fetch_snapshot(profile_url, name, html_file=None):
    parsed = urlparse(profile_url)
    users = parse_qs(parsed.query).get("user", [])
    if parsed.scheme != "https" or parsed.netloc != "scholar.google.com" or len(users) != 1:
        raise ValueError("Expected a public scholar.google.com profile URL")
    user = users[0]
    papers = []
    identities = set()
    total = None
    for start in range(0, 10000, 100):
        if html_file:
            if start:
                raise ValueError("Saved HTML is incomplete: Show more is still enabled")
            html = Path(html_file).read_bytes()
        else:
            url = "https://scholar.google.com/citations?" + urlencode(
                {"user": user, "hl": "en", "cstart": start, "pagesize": 100}
            )
            request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
            with urlopen(request, timeout=30) as response:
                html = response.read()
        page = parse_page(html, user, name)
        if total is not None and page.total != total:
            raise ValueError("Scholar total changed during pagination; retry on the next run")
        total = page.total
        for paper in page.papers:
            if paper.identity in identities:
                raise ValueError("Repeated Scholar rows; pagination may be incomplete")
            identities.add(paper.identity)
            papers.append(paper)
        if not page.has_more:
            return total, papers
        time.sleep(1)
    raise ValueError("Scholar pagination exceeded the supported limit")


def badge(paper):
    cites = ",".join(paper.clusters)
    return (f" [![Citations: {paper.citations}](https://img.shields.io/badge/"
            f"Citations-{paper.citations}-ffc107?style=flat)]"
            f"(https://scholar.google.com/scholar?oi=bibs&hl=en&cites={cites})")


def update_publications(source, papers):
    lines = []
    matched = 0
    for line in source.splitlines(keepends=True):
        publication = PUBLICATION.match(line)
        if not publication:
            lines.append(line)
            continue
        old_badge = BADGE.search(line)
        existing_clusters = cluster_ids(old_badge[0].split("](")[-1][:-1]) if old_badge else ()
        candidates = [p for p in papers if set(existing_clusters).intersection(p.clusters)]
        if not candidates:
            candidates = [p for p in papers if normalize(p.title) == normalize(publication[1])]
        if len(candidates) != 1:
            if old_badge or candidates:
                raise ValueError(f"Missing or ambiguous match for publication: {publication[1]}")
            print(f"Warning: no Scholar match; leaving publication unchanged: {publication[1]}", file=sys.stderr)
            lines.append(line)
            continue
        matched += 1
        paper = candidates[0]
        replacement = badge(paper) if paper.citations > 30 else ""
        if old_badge:
            # Keep an existing merged cited-by URL intact when its IDs still match.
            if replacement and set(existing_clusters) == set(paper.clusters):
                replacement = re.sub(r"Citations(?:: |-)[0-9]+", lambda m: m[0].rstrip("0123456789") + str(paper.citations), old_badge[0])
            line = line[:old_badge.start()] + replacement + line[old_badge.end():]
        elif replacement:
            line = line.rstrip("\r\n") + replacement + line[len(line.rstrip("\r\n")):]
        lines.append(line)
    if not matched:
        raise ValueError("No homepage publications matched the Scholar snapshot")
    return "".join(lines), matched


def replace_field(source, key, value):
    result, count = re.subn(r"(^  " + key + r"\s*:\s*).*$", lambda m: m[1] + value, source, flags=re.M)
    if count != 1:
        raise ValueError(f"Expected exactly one author.{key} field")
    return result


def update_repository(root, html_file=None, check=False):
    config_path = root / "_config.yml"
    publications_path = root / "_includes/about/publications.md"
    config = config_path.read_text(encoding="utf-8")
    publications = publications_path.read_text(encoding="utf-8")
    total, papers = fetch_snapshot(scalar(config, "googlescholar"), scalar(config, "name"), html_file)
    new_publications, matched = update_publications(publications, papers)
    new_config = replace_field(config, "scholar_citations", str(total))
    changed = new_config != config or new_publications != publications
    print(f"Scholar: {total} citations, {len(papers)} articles; matched {matched} homepage publications")
    if not changed:
        print("Citation data unchanged; keeping the existing snapshot date")
        return False
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    new_config = replace_field(new_config, "scholar_citations_updated", f'"{today}"')
    new_publications, count = re.subn(
        r"(<!-- Google Scholar citation snapshot, checked )\d{4}-\d{2}-\d{2}",
        lambda m: m[1] + today, new_publications,
    )
    if count != 1:
        raise ValueError("Expected exactly one publication snapshot comment")
    if check:
        print("Citation update available (--check: no files written)")
    else:
        config_path.write_text(new_config, encoding="utf-8")
        publications_path.write_text(new_publications, encoding="utf-8")
        print(f"Updated citation snapshot for {today}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-file", type=Path, help="Use a saved, complete Scholar profile page")
    parser.add_argument("--check", action="store_true", help="Validate and report changes without writing files")
    args = parser.parse_args()
    try:
        update_repository(Path(__file__).resolve().parents[2], args.html_file, args.check)
    except Exception as error:
        print(f"Citation update failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
