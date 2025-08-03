#!/usr/bin/env python3
"""
arXiv MCP Server
Adds a download_pdf tool to the earlier implementation.
"""

import os
import pathlib
import datetime as _dt
import urllib.parse as _up
from typing import List, Dict

import requests
import feedparser
from fastmcp import FastMCP

BASE_URL = "http://export.arxiv.org/api/query"
HEADERS = {
    "User-Agent": "oneshot-research-assistant"  # replace with a real contact
}

mcp = FastMCP("arxiv")

def _build_url(*, search_query: str = "",
               id_list: str = "",
               start: int = 0,
               max_results: int = 10,
               sort_by: str = "relevance",
               sort_order: str = "descending") -> str:
    qs = {
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order
    }
    if search_query:
        qs["search_query"] = search_query
    elif id_list:
        qs["id_list"] = id_list
    else:
        raise ValueError("Either search_query or id_list must be supplied")

    return f"{BASE_URL}?{_up.urlencode(qs)}"


def _entry_to_dict(entry) -> Dict:
    pdf_link = next(
        (l.href for l in entry.links
         if l.rel == "related" and l.type == "application/pdf"),
        None
    )
    return {
        "arxiv_id": entry.id.split("/")[-1],
        "title": entry.title.strip(),
        "summary": entry.summary.strip(),
        "authors": [a.name for a in entry.authors],
        "published": entry.published,
        "updated": entry.updated,
        "primary_category": entry.tags[0]["term"] if entry.tags else None,
        "categories": [t["term"] for t in entry.tags] if entry.tags else [],
        "pdf_url": pdf_link,
        "html_url": next((l.href for l in entry.links if l.rel == "alternate"), None)
    }


def _query_arxiv(url: str) -> List[Dict]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    return [_entry_to_dict(e) for e in feed.entries]


@mcp.tool()
def search_arxiv(query: str,
                 start: int = 0,
                 max_results: int = 10,
                 sort_by: str = "relevance",
                 sort_order: str = "descending") -> Dict:
    """
    Search for papers on arXiv using the arXiv API.
    
    Args:
        query: Search query string. Supports arXiv search syntax including:
               - Author names: "au:Smith"
               - Title words: "ti:machine learning"
               - Abstract words: "abs:neural networks"
               - Categories: "cat:cs.AI" or "cat:cs.AI+cs.LG"
               - Date ranges: "submittedDate:20230101+20231231"
               - Full text: "all:quantum computing"
        start: Starting position for pagination (0-based)
        max_results: Maximum number of results to return (1-100, default 10)
        sort_by: Sort method - "relevance", "lastUpdatedDate", "submittedDate"
        sort_order: Sort direction - "ascending" or "descending"
        
    Returns:
        Dict containing:
        - query: The original search query
        - results: List of paper dictionaries with fields:
          * arxiv_id: arXiv identifier (e.g., "2307.12345")
          * title: Paper title
          * summary: Abstract text
          * authors: List of author names
          * published: Publication date
          * updated: Last update date
          * primary_category: Main arXiv category
          * categories: List of all categories
          * pdf_url: Direct PDF download link
          * html_url: arXiv HTML page link
          
    Examples:
        - search_arxiv("machine learning", max_results=5)
        - search_arxiv("au:Hinton+cat:cs.AI", sort_by="submittedDate")
        - search_arxiv("ti:transformer+abs:attention", max_results=20)
    """
    url = _build_url(search_query=query,
                     start=start,
                     max_results=max_results,
                     sort_by=sort_by,
                     sort_order=sort_order)
    results = _query_arxiv(url)
    return {"query": query, "results": results}


@mcp.tool()
def get_paper_metadata(arxiv_ids: List[str]) -> Dict:
    """
    Retrieve detailed metadata for specific arXiv papers by their IDs.
    
    Args:
        arxiv_ids: List of arXiv identifiers. Each ID can be:
                   - Basic ID: "2307.12345"
                   - Versioned ID: "2307.12345v2"
                   - Full URL ID: "http://arxiv.org/abs/2307.12345"
                   
    Returns:
        Dict containing:
        - count: Number of papers successfully retrieved
        - papers: List of paper dictionaries with complete metadata:
          * arxiv_id: arXiv identifier
          * title: Paper title
          * summary: Abstract text
          * authors: List of author names
          * published: Publication date
          * updated: Last update date
          * primary_category: Main arXiv category
          * categories: List of all categories
          * pdf_url: Direct PDF download link
          * html_url: arXiv HTML page link
          
    Examples:
        - get_paper_metadata(["2307.12345", "2308.98765"])
        - get_paper_metadata(["2307.12345v2"])
        
    Note:
        - Returns error if no arXiv IDs provided
        - Invalid IDs are ignored (no error thrown)
        - Maximum 100 IDs per request (arXiv API limit)
    """
    if not arxiv_ids:
        return {"error": "At least one arXiv ID is required", "papers": []}

    id_param = ",".join(arxiv_ids)
    url = _build_url(id_list=id_param)
    papers = _query_arxiv(url)
    return {"count": len(papers), "papers": papers}


@mcp.tool()
def download_pdf(arxiv_id: str,
                 dest_dir: str = "downloads") -> Dict:
    """
    Download a paper's PDF from arXiv and save it locally.
    
    Args:
        arxiv_id: arXiv identifier. Can be:
                  - Basic ID: "2307.12345"
                  - Versioned ID: "2307.12345v2"
                  - Full URL: "http://arxiv.org/abs/2307.12345"
        dest_dir: Local directory path for storing PDFs. 
                  Directory will be created if it doesn't exist.
                  Default: "downloads"
                  
    Returns:
        Dict containing:
        - arxiv_id: The arXiv identifier used
        - pdf_url: The URL where PDF was downloaded from
        - local_path: Full path to the saved PDF file
        - size_bytes: Size of the downloaded file in bytes
        
        Or error dict with:
        - error: Error message describing the failure
        - arxiv_id: The arXiv identifier that failed
        
    Examples:
        - download_pdf("2307.12345")
        - download_pdf("2307.12345v2", "papers/quantum")
        - download_pdf("http://arxiv.org/abs/2307.12345", "research")
        
    Note:
        - Downloads from https://arxiv.org/pdf/{arxiv_id}.pdf
        - File is saved as "{arxiv_id}.pdf" in dest_dir
        - Uses streaming download for large files
        - 60-second timeout for download requests
        - Returns error for HTTP 4xx/5xx responses
    """
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    # Ensure target directory exists
    dest_path = pathlib.Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    file_path = dest_path / f"{arxiv_id}.pdf"

    try:
        with requests.get(pdf_url, headers=HEADERS, stream=True, timeout=60) as r:
            if r.status_code != 200:
                return {
                    "error": f"Failed to fetch PDF (HTTP {r.status_code})",
                    "arxiv_id": arxiv_id
                }

            # Write the file in chunks
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return {
            "arxiv_id": arxiv_id,
            "pdf_url": pdf_url,
            "local_path": str(file_path.resolve()),
            "size_bytes": file_path.stat().st_size
        }

    except requests.RequestException as e:
        return {
            "error": f"Request failed: {e}",
            "arxiv_id": arxiv_id
        }



if __name__ == "__main__":
    mcp.run()
