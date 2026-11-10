#!/usr/bin/env python3
"""
free_corbis_mcp.py — a $0, no-API-key drop-in replacement for the Corbis MCP server.

Exposes the same Tier-1 tool *names* the venue workflow skills call
(search_papers, get_paper_details, get_paper_details_batch, top_cited_articles,
search_datasets, format_citation, export_citations, fred_search,
fred_series_batch, find_academic_identity), backed by free, keyless sources:

  - OpenAlex   (https://api.openalex.org)        — papers, authors, citations
  - FRED CSV   (fredgraph.csv)                    — macro time series, no key
  - Crossref   (https://api.crossref.org)         — DOI fallback metadata

The proprietary CRE market tools (get_market_data, compare_markets,
search_markets, get_national_macro, get_market_trends) have no free equivalent;
they are registered but return a clear "not available" message so skills degrade
gracefully instead of crashing.

Transport: MCP stdio, newline-delimited JSON-RPC 2.0. Pure stdlib (no pip deps).
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MAILTO = "kyle.ngnq@gmail.com"  # OpenAlex "polite pool" — faster, courteous
UA = f"free-corbis-mcp/0.1 (mailto:{MAILTO})"
SERVER_NAME = "corbis"
SERVER_VERSION = "0.1.0-free"


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #
def _fetch(url, timeout, accept=None):
    """GET with retry/backoff — OpenAlex returns transient 503s and slow cold starts."""
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    last = None
    attempts = 6
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:  # noqa: PERF203
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < attempts - 1:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = e
            if attempt < attempts - 1:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise
    raise last  # pragma: no cover


def _get(url, timeout=60):
    return json.loads(_fetch(url, timeout, accept="application/json"))


def _get_text(url, timeout=60):
    return _fetch(url, timeout)


def _oa(path, params):
    params = {k: v for k, v in params.items() if v is not None}
    params["mailto"] = MAILTO
    return _get("https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(params))


# --------------------------------------------------------------------------- #
# OpenAlex -> Corbis paper-shape mapping
# --------------------------------------------------------------------------- #
def _short_id(oa_id):
    if not oa_id:
        return None
    return oa_id.rsplit("/", 1)[-1]  # https://openalex.org/W123 -> W123


def _abstract(work):
    inv = work.get("abstract_inverted_index")
    if not inv:
        return None
    positions = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def _journal(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name")


def _map_work(work, compact=False):
    sid = _short_id(work.get("id"))
    doi = work.get("doi")
    out = {
        "id": sid,
        "openalexId": sid,
        "title": work.get("title"),
        "authors": [a["author"]["display_name"] for a in work.get("authorships", []) if a.get("author")],
        "year": work.get("publication_year"),
        "journal": _journal(work),
        "doi": doi.replace("https://doi.org/", "") if doi else None,
        "url": doi or (work.get("id")),
        "citedByCount": work.get("cited_by_count"),
    }
    if not compact:
        out["abstract"] = _abstract(work)
    return out


_SOURCE_CACHE = {}


def _norm_source_name(name):
    """Fold the variations OpenAlex and citing authors disagree about.

    A leading article and '&' vs 'and' are the only differences tolerated.
    Everything else has to match, because the near misses in this corpus are
    different journals: 'Review of Finance' against 'International Review of
    Economics & Finance' is two words apart and 5,991 works apart.
    """
    s = " ".join(str(name).strip().lower().split())
    for article in ("the ", "a "):
        if s.startswith(article):
            s = s[len(article):]
    return s.replace("&", "and").replace("  ", " ")


def _resolve_source_ids(names):
    """Map journal display names to OpenAlex source IDs (Sxxxx).

    Returns (ids, matched, unmatched). A name resolves ONLY on an exact
    display-name match after `_norm_source_name`; anything else is returned as
    unmatched for the caller to report.

    This once took the first fuzzy hit with no name check, so
    `Review of Finance` resolved to *International Review of Economics &
    Finance* and every downstream pull silently ran against the wrong journal.
    The 2026-06 calibration build is the known casualty: 16 accounting venues
    and 14 out-of-scope ones entered a finance anchor as analogs. A resolver
    that guesses is worse than one that fails, because a wrong journal id
    produces confident, plausible, wrong results all the way downstream.

    (`per-page` was also being sent instead of `per_page`, so the limit was
    ignored and OpenAlex returned its default page. That is why the bad hit was
    always available to be picked.)

    Transport errors PROPAGATE. They used to be swallowed into `None`, which
    reported "no such journal" when the truth was "could not ask" -- the same
    false negative as the substitution bug, pointing the other way. A caller
    that cannot reach OpenAlex needs to know that, not receive a confident
    empty answer.
    """
    ids, matched, unmatched = [], [], []
    for name in names:
        key = _norm_source_name(name)
        if key not in _SOURCE_CACHE:
            data = _oa("sources", {"search": name, "per_page": 25})
            hit = next((r for r in data.get("results", [])
                        if _norm_source_name(r.get("display_name")) == key), None)
            _SOURCE_CACHE[key] = _short_id(hit["id"]) if hit else None
        sid = _SOURCE_CACHE[key]
        if sid:
            ids.append(sid)
            matched.append(name)
        else:
            unmatched.append(name)
    return ids, matched, unmatched


def _year_filter(min_year, max_year):
    parts = []
    if min_year:
        parts.append(f"from_publication_date:{int(min_year)}-01-01")
    if max_year:
        parts.append(f"to_publication_date:{int(max_year)}-12-31")
    return ",".join(parts) if parts else None


# --------------------------------------------------------------------------- #
# Tool implementations
# --------------------------------------------------------------------------- #
def t_search_papers(args):
    query = args["query"]
    match_count = min(int(args.get("matchCount", 10)), 20)
    sort_by = args.get("sortBy", "relevance")
    journals = args.get("journalNames") or []

    flt_parts = []
    yf = _year_filter(args.get("minYear"), args.get("maxYear"))
    if yf:
        flt_parts.append(yf)
    unmatched = []
    if journals:
        ids, _matched, unmatched = _resolve_source_ids(journals)
        if ids:
            flt_parts.append("primary_location.source.id:" + "|".join(ids))
    flt = ",".join(flt_parts) if flt_parts else None

    # For "year" we let OpenAlex sort server-side. For "relevance"/"citedByCount" we
    # keep OpenAlex's topical relevance ranking, over-fetch, then re-rank by citations
    # locally if asked — avoids returning a mega-cited but off-topic keyword match.
    server_sort = "publication_year:desc" if sort_by == "year" else None
    over = 3 if sort_by == "citedByCount" else 1
    per_page = min(max(match_count * over, match_count), 50)
    data = _oa("works", {"search": query, "sort": server_sort, "per-page": per_page, "filter": flt})
    results = [_map_work(w, compact=args.get("compact", False)) for w in data.get("results", [])]
    if sort_by == "citedByCount":
        results.sort(key=lambda r: r.get("citedByCount") or 0, reverse=True)
    results = results[:match_count]
    out = {"results": results, "totalAvailable": data.get("meta", {}).get("count"), "_source": "openalex"}
    if unmatched:
        out["journalsUnmatched"] = unmatched
    return out


def _normalize_paper_id(pid):
    pid = pid.strip()
    if pid.lower().startswith("w") and pid[1:].isdigit():
        return "works/" + pid.upper()
    if "openalex.org/" in pid:
        return "works/" + _short_id(pid)
    if pid.startswith("10.") or "doi.org/" in pid:
        doi = pid.split("doi.org/")[-1]
        return "works/https://doi.org/" + doi
    return "works/" + pid


def _fetch_one(pid):
    work = _oa(_normalize_paper_id(pid), {})
    mapped = _map_work(work, compact=False)
    mapped["fullText"] = None  # OpenAlex provides metadata + abstract, not full text
    mapped["metadata"] = {
        "type": work.get("type"),
        "is_oa": (work.get("open_access") or {}).get("is_oa"),
        "referenced_works_count": len(work.get("referenced_works", [])),
        "concepts": [c["display_name"] for c in work.get("concepts", [])[:6]],
    }
    return mapped


def t_get_paper_details(args):
    pid = args.get("paperId") or args.get("id")
    return _fetch_one(pid)


def t_get_paper_details_batch(args):
    ids = (args.get("paperIds") or args.get("ids") or [])[:25]
    results, errors = [], []
    for pid in ids:
        try:
            r = _fetch_one(pid)
            r["requestedId"] = pid
            results.append(r)
        except Exception as e:  # noqa: BLE001
            errors.append({"paperId": pid, "error": str(e)})
    return {"results": results, "errors": errors, "totalRequested": len(ids), "totalFound": len(results)}


def t_top_cited_articles(args):
    journals = args.get("journalNames") or []
    if not journals:
        return {"error": "journalNames is required", "results": []}
    query = args.get("query")
    limit = min(int(args.get("limit", 10)), 50)
    ids, matched, unmatched = _resolve_source_ids(journals)
    if not ids:
        return {"results": [], "journalsMatched": [], "journalsUnmatched": unmatched,
                "totalFound": 0, "note": "No journals resolved to OpenAlex sources."}
    flt_parts = ["primary_location.source.id:" + "|".join(ids)]
    yf = _year_filter(args.get("minYear"), args.get("maxYear"))
    if yf:
        flt_parts.append(yf)
    params = {"filter": ",".join(flt_parts), "sort": "cited_by_count:desc",
              "per-page": min(limit, 50)}
    if query:
        params["search"] = query
    data = _oa("works", params)
    compact = args.get("compact", True)
    results = [_map_work(w, compact=compact) for w in data.get("results", [])][:limit]
    for i, r in enumerate(results, 1):
        r["rank"] = i
    return {"results": results, "journalsMatched": matched, "journalsUnmatched": unmatched,
            "totalFound": data.get("meta", {}).get("count")}


# Curated, keyless FRED series map (covers the common macro-finance asks).
_FRED_MAP = [
    ("UNRATE", "Unemployment Rate", "Monthly", "Percent", ["unemployment", "jobless", "labor"]),
    ("PAYEMS", "All Employees, Total Nonfarm (Payrolls)", "Monthly", "Thousands", ["payroll", "employment", "jobs", "nonfarm"]),
    ("GDP", "Gross Domestic Product", "Quarterly", "Billions USD", ["gdp", "output", "gross domestic"]),
    ("GDPC1", "Real Gross Domestic Product", "Quarterly", "Billions Chained USD", ["real gdp", "gdp", "output"]),
    ("CPIAUCSL", "CPI for All Urban Consumers: All Items", "Monthly", "Index 1982-84=100", ["cpi", "inflation", "consumer price"]),
    ("PCEPI", "PCE Price Index", "Monthly", "Index", ["pce", "inflation", "deflator"]),
    ("FEDFUNDS", "Effective Federal Funds Rate", "Monthly", "Percent", ["fed funds", "policy rate", "interest rate", "federal funds"]),
    ("DGS10", "10-Year Treasury Constant Maturity Rate", "Daily", "Percent", ["10 year", "treasury", "yield", "10-year"]),
    ("DGS2", "2-Year Treasury Constant Maturity Rate", "Daily", "Percent", ["2 year", "treasury", "yield", "2-year"]),
    ("T10Y2Y", "10Y-2Y Treasury Spread", "Daily", "Percent", ["yield curve", "spread", "term spread", "inversion"]),
    ("MORTGAGE30US", "30-Year Fixed Rate Mortgage Average", "Weekly", "Percent", ["mortgage", "30 year mortgage", "housing finance"]),
    ("CSUSHPISA", "S&P/Case-Shiller U.S. National Home Price Index", "Monthly", "Index", ["home price", "house price", "case shiller", "housing"]),
    ("HOUST", "Housing Starts: Total New Privately-Owned", "Monthly", "Thousands", ["housing starts", "construction", "residential"]),
    ("VIXCLS", "CBOE Volatility Index: VIX", "Daily", "Index", ["vix", "volatility", "fear"]),
    ("SP500", "S&P 500", "Daily", "Index", ["s&p 500", "sp500", "stock market", "equity index"]),
    ("BAMLH0A0HYM2", "ICE BofA US High Yield Index OAS", "Daily", "Percent", ["credit spread", "high yield", "oas", "credit"]),
    ("DEXUSEU", "USD/EUR Exchange Rate", "Daily", "USD per EUR", ["exchange rate", "dollar euro", "fx", "currency"]),
    ("M2SL", "M2 Money Stock", "Monthly", "Billions USD", ["money supply", "m2", "monetary"]),
    ("INDPRO", "Industrial Production Index", "Monthly", "Index", ["industrial production", "manufacturing", "output"]),
    ("UMCSENT", "U. of Michigan Consumer Sentiment", "Monthly", "Index", ["consumer sentiment", "confidence", "michigan"]),
]


def t_fred_search(args):
    q = args.get("query", "").lower()
    limit = min(int(args.get("limit", 10)), 50)
    scored = []
    for sid, title, freq, units, kws in _FRED_MAP:
        score = sum(1 for k in kws if k in q) + (2 if sid.lower() in q else 0)
        if title.lower() in q or any(w in title.lower() for w in q.split() if len(w) > 3):
            score += 1
        if score:
            scored.append((score, {"id": sid, "title": title, "frequency": freq, "units": units}))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [r for _, r in scored[:limit]]
    note = None
    if not results:
        note = ("No match in the curated keyless map. If you know the FRED series ID, call "
                "fred_series_batch directly. Full search needs a free FRED API key.")
        results = [{"id": r[0], "title": r[1], "frequency": r[2], "units": r[3]} for r in
                   [(x[0], x[1], x[2], x[3]) for x in _FRED_MAP][:limit]]
    return {"results": results, "_source": "curated+fredgraph", "note": note}


def t_fred_series_batch(args):
    items = args.get("items") or []
    series = []
    per_series = []
    for it in items[:15]:
        sid = it.get("seriesId")
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=" + urllib.parse.quote(sid)
        if it.get("observationStart"):
            url += "&cosd=" + it["observationStart"]
        if it.get("observationEnd"):
            url += "&coed=" + it["observationEnd"]
        try:
            csv = _get_text(url)
            rows = [ln.split(",") for ln in csv.strip().splitlines()]
            header = rows[0]
            obs = []
            for r in rows[1:]:
                if len(r) >= 2 and r[1] not in (".", ""):
                    obs.append({"date": r[0], "value": float(r[1])})
            series.append({"seriesId": sid, "columns": header, "observations": obs,
                           "count": len(obs)})
            per_series.append({"seriesId": sid, "status": "ok", "count": len(obs)})
        except Exception as e:  # noqa: BLE001
            per_series.append({"seriesId": sid, "status": "error", "error": str(e)})
    return {"ok": all(p["status"] == "ok" for p in per_series), "seriesCount": len(series),
            "perSeries": per_series, "series": series, "_source": "fredgraph.csv"}


# Curated free finance datasets (mirrors what search_datasets surfaces).
_DATASETS = [
    {"name": "Ken French Data Library", "description": "Factor returns (FF3/FF5, momentum), portfolios.",
     "link": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html",
     "accessInfo": "Free download", "dataType": "asset pricing", "tags": ["factors", "returns", "asset-pricing"]},
    {"name": "FRED", "description": "800k+ US/intl macroeconomic time series.",
     "link": "https://fred.stlouisfed.org", "accessInfo": "Free; CSV keyless", "dataType": "macro",
     "tags": ["macro", "rates", "inflation"]},
    {"name": "SEC EDGAR", "description": "Company filings (10-K, 10-Q, 8-K), full-text search, XBRL.",
     "link": "https://www.sec.gov/edgar", "accessInfo": "Free API", "dataType": "filings",
     "tags": ["filings", "fundamentals", "corporate"]},
    {"name": "OpenAlex", "description": "250M+ scholarly works, authors, citations.",
     "link": "https://openalex.org", "accessInfo": "Free API, no key", "dataType": "bibliometric",
     "tags": ["papers", "citations", "bibliometrics"]},
    {"name": "WRDS (open subset)", "description": "Some open datasets; full access needs subscription.",
     "link": "https://wrds-www.wharton.upenn.edu", "accessInfo": "Subscription", "dataType": "finance",
     "tags": ["crsp", "compustat", "finance"]},
    {"name": "Yahoo Finance / yfinance", "description": "Historical equity, ETF, FX, crypto prices.",
     "link": "https://github.com/ranaroussi/yfinance", "accessInfo": "Free (unofficial)", "dataType": "prices",
     "tags": ["prices", "equities", "market-data"]},
    {"name": "Federal Reserve H.15 / Treasury", "description": "Daily yield curve, rates.",
     "link": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates",
     "accessInfo": "Free", "dataType": "rates", "tags": ["rates", "treasury", "yield-curve"]},
    {"name": "FHFA House Price Index", "description": "US house price indices by region/metro.",
     "link": "https://www.fhfa.gov/data/hpi", "accessInfo": "Free download", "dataType": "housing",
     "tags": ["housing", "real-estate", "prices"]},
]


def t_search_datasets(args):
    q = (args.get("query") or "").lower()
    topic = (args.get("topicFilter") or "").lower()
    limit = min(int(args.get("matchCount", 5)), 20)
    terms = [w for w in (q + " " + topic).split() if len(w) > 2]
    scored = []
    for d in _DATASETS:
        hay = (d["name"] + " " + d["description"] + " " + " ".join(d["tags"])).lower()
        score = sum(1 for t in terms if t in hay)
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return {"results": [d for _, d in scored[:limit]], "_source": "curated-free-datasets"}


# --------------------------------------------------------------------------- #
# Local citation formatting (no API)
# --------------------------------------------------------------------------- #
def _bibkey(p):
    a = (p.get("authors") or ["anon"])[0].split()[-1].lower()
    a = "".join(c for c in a if c.isalnum()) or "anon"
    return f"{a}{p.get('year','')}"


def _bibtex_one(p):
    fields = []
    if p.get("authors"):
        fields.append(("author", " and ".join(p["authors"])))
    for k in ("title", "year", "journal", "volume", "number", "pages", "publisher"):
        if p.get(k):
            fields.append((k if k != "number" else "number", str(p[k])))
    if p.get("doi"):
        fields.append(("doi", p["doi"]))
    if p.get("url"):
        fields.append(("url", p["url"]))
    body = ",\n  ".join(f"{k} = {{{v}}}" for k, v in fields)
    return f"@article{{{_bibkey(p)},\n  {body}\n}}"


def _apa_one(p):
    authors = p.get("authors") or []
    if len(authors) > 1:
        astr = ", ".join(authors[:-1]) + ", & " + authors[-1]
    else:
        astr = authors[0] if authors else "Anonymous"
    out = f"{astr} ({p.get('year','n.d.')}). {p.get('title','')}."
    if p.get("journal"):
        out += f" {p['journal']}."
    if p.get("doi"):
        out += f" https://doi.org/{p['doi']}"
    return out


def t_format_citation(args):
    papers = args.get("papers") or []
    style = (args.get("style") or "bibtex").lower()
    fmt = {"bibtex": _bibtex_one, "apa": _apa_one}.get(style, _apa_one)
    citations = [fmt(p) for p in papers]
    return {"citations": citations, "style": style, "count": len(citations)}


def t_export_citations(args):
    papers = args.get("citations") or args.get("papers") or []
    formats = args.get("formats") or ["bibtex", "markdown"]
    base = args.get("fileName") or "references"
    exports = []
    if "bibtex" in formats:
        content = "\n\n".join(_bibtex_one(p) for p in papers) + "\n"
        exports.append({"format": "bibtex", "filename": base + ".bib", "content": content,
                        "bytes": len(content)})
    if "markdown" in formats:
        content = "\n".join("- " + _apa_one(p) for p in papers) + "\n"
        exports.append({"format": "markdown", "filename": base + ".md", "content": content,
                        "bytes": len(content)})
    if "json" in formats:
        content = json.dumps(papers, indent=2)
        exports.append({"format": "json", "filename": base + ".json", "content": content,
                        "bytes": len(content)})
    return {"exports": exports}


def t_find_academic_identity(args):
    name = args.get("nameOverride")
    if not name:
        return {"status": "no_name", "candidate": None,
                "note": "Pass nameOverride to search OpenAlex authors."}
    data = _oa("authors", {"search": name, "per-page": 1})
    rows = data.get("results", [])
    if not rows:
        return {"status": "not_found", "candidate": None}
    a = rows[0]
    inst = ((a.get("last_known_institutions") or [{}])[0] or {}).get("display_name")
    return {"status": "ok", "candidate": {
        "authorId": _short_id(a.get("id")), "name": a.get("display_name"),
        "institution": inst, "hIndex": (a.get("summary_stats") or {}).get("h_index"),
        "citedByCount": a.get("cited_by_count"), "papersCount": a.get("works_count")}}


def _unavailable(name):
    def _fn(args):
        return {"error": "unavailable_in_free_shim",
                "message": (f"'{name}' uses proprietary Corbis commercial-real-estate data "
                            "with no free equivalent. Skip CRE-specific steps or use a paid "
                            "Corbis key for these.")}
    return _fn


# --------------------------------------------------------------------------- #
# Tool registry
# --------------------------------------------------------------------------- #
TOOLS = {
    "search_papers": (t_search_papers, "Search ~250M papers via OpenAlex (keyless).",
                      {"query": {"type": "string"}, "matchCount": {"type": "number"},
                       "minYear": {"type": "number"}, "maxYear": {"type": "number"},
                       "journalNames": {"type": "array", "items": {"type": "string"}},
                       "sortBy": {"type": "string", "enum": ["relevance", "citedByCount", "year"]},
                       "compact": {"type": "boolean"}}, ["query"]),
    "get_paper_details": (t_get_paper_details, "Full metadata for one paper (OpenAlex ID, DOI, or URL).",
                          {"paperId": {"type": "string"}}, ["paperId"]),
    "get_paper_details_batch": (t_get_paper_details_batch, "Fetch up to 25 papers at once.",
                                {"paperIds": {"type": "array", "items": {"type": "string"}}}, ["paperIds"]),
    "top_cited_articles": (t_top_cited_articles, "Most-cited papers within given journals.",
                           {"journalNames": {"type": "array", "items": {"type": "string"}},
                            "query": {"type": "string"}, "minYear": {"type": "number"},
                            "maxYear": {"type": "number"}, "limit": {"type": "number"},
                            "compact": {"type": "boolean"}}, ["journalNames"]),
    "search_datasets": (t_search_datasets, "Search curated free finance datasets.",
                        {"query": {"type": "string"}, "matchCount": {"type": "number"},
                         "topicFilter": {"type": "string"}, "regionFilter": {"type": "string"}}, ["query"]),
    "fred_search": (t_fred_search, "Find FRED macro series IDs (curated keyless map).",
                    {"query": {"type": "string"}, "limit": {"type": "number"}}, ["query"]),
    "fred_series_batch": (t_fred_series_batch, "Fetch FRED time series via keyless fredgraph CSV.",
                          {"items": {"type": "array", "items": {"type": "object"}}}, ["items"]),
    "format_citation": (t_format_citation, "Format papers as BibTeX/APA.",
                        {"papers": {"type": "array", "items": {"type": "object"}},
                         "style": {"type": "string"}}, ["papers", "style"]),
    "export_citations": (t_export_citations, "Export bibliography files (BibTeX/Markdown/JSON).",
                         {"citations": {"type": "array", "items": {"type": "object"}},
                          "formats": {"type": "array", "items": {"type": "string"}},
                          "fileName": {"type": "string"}}, ["citations"]),
    "find_academic_identity": (t_find_academic_identity, "Find an OpenAlex author profile.",
                               {"nameOverride": {"type": "string"}}, []),
    # CRE market tools — registered but unavailable for free.
    "get_market_data": (_unavailable("get_market_data"), "[unavailable in free shim]", {}, []),
    "compare_markets": (_unavailable("compare_markets"), "[unavailable in free shim]", {}, []),
    "search_markets": (_unavailable("search_markets"), "[unavailable in free shim]", {}, []),
    "get_national_macro": (_unavailable("get_national_macro"), "[unavailable in free shim]", {}, []),
    "get_market_trends": (_unavailable("get_market_trends"), "[unavailable in free shim]", {}, []),
}


def _tool_list():
    out = []
    for name, (_fn, desc, props, required) in TOOLS.items():
        out.append({"name": name, "description": desc,
                    "inputSchema": {"type": "object", "properties": props, "required": required}})
    return out


# --------------------------------------------------------------------------- #
# JSON-RPC / MCP stdio loop
# --------------------------------------------------------------------------- #
def _send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _result(rid, result):
    _send({"jsonrpc": "2.0", "id": rid, "result": result})


def _error(rid, code, message):
    _send({"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}})


def handle(msg):
    method = msg.get("method")
    rid = msg.get("id")
    if method == "initialize":
        _result(rid, {"protocolVersion": "2024-11-05",
                      "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                      "capabilities": {"tools": {"listChanged": False}}})
    elif method == "notifications/initialized":
        pass  # notification, no response
    elif method == "ping":
        _result(rid, {})
    elif method == "tools/list":
        _result(rid, {"tools": _tool_list()})
    elif method in ("resources/list", "prompts/list"):
        _result(rid, {"resources": []} if method == "resources/list" else {"prompts": []})
    elif method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        entry = TOOLS.get(name)
        if not entry:
            _error(rid, -32601, f"Unknown tool: {name}")
            return
        try:
            payload = entry[0](args)
            _result(rid, {"content": [{"type": "text", "text": json.dumps(payload)}],
                          "isError": bool(payload.get("error")) if isinstance(payload, dict) else False})
        except Exception as e:  # noqa: BLE001
            _result(rid, {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                          "isError": True})
    elif rid is not None:
        _error(rid, -32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        handle(msg)


if __name__ == "__main__":
    main()
