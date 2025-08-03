#!/usr/bin/env python3
"""
bioRxiv MCP Server
Provides access to bioRxiv and medRxiv preprint servers via their REST API.
"""

import os
import pathlib
import datetime as _dt
import urllib.parse as _up
from typing import List, Dict, Optional, Literal, Union
from datetime import datetime, timedelta

import requests
from fastmcp import FastMCP

BASE_URL = "https://api.biorxiv.org"
HEADERS = {
    "User-Agent": "oneshot-research-assistant"
}

mcp = FastMCP("biorxiv")

def _build_details_url(server: str, interval: str, cursor: int = 0, 
                      category: Optional[str] = None) -> str:
    """Build URL for details endpoint."""
    url = f"{BASE_URL}/details/{server}/{interval}/{cursor}"
    if category:
        # URL encode the category or replace spaces with underscores
        category_encoded = _up.quote(category.replace(' ', '_'))
        url += f"?category={category_encoded}"
    return url

def _build_doi_url(server: str, doi: str) -> str:
    """Build URL for single DOI lookup."""
    return f"{BASE_URL}/details/{server}/{doi}/na"

def _build_pubs_url(server: str, interval: str, cursor: int = 0) -> str:
    """Build URL for published papers endpoint."""
    return f"{BASE_URL}/pubs/{server}/{interval}/{cursor}"

def _build_funder_url(server: str, interval: str, funder_ror_id: str, 
                     cursor: int = 0, category: Optional[str] = None) -> str:
    """Build URL for funder-filtered papers."""
    url = f"{BASE_URL}/funder/{server}/{interval}/{funder_ror_id}/{cursor}"
    if category:
        category_encoded = _up.quote(category.replace(' ', '_'))
        url += f"?category={category_encoded}"
    return url

def _query_biorxiv(url: str) -> Dict:
    """Make API request and return JSON response."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except ValueError as e:
        return {"error": f"Invalid JSON response: {str(e)}"}

def _format_date_range(start_date: str, end_date: str) -> str:
    """Format date range for API (YYYY-MM-DD/YYYY-MM-DD)."""
    return f"{start_date}/{end_date}"

def _validate_date_format(date_str: str) -> bool:
    """Validate date format is YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def _determine_interval(start_date: Optional[str], end_date: Optional[str], 
                       recent_days: Optional[Union[int, str]], 
                       recent_count: Optional[Union[int, str]]) -> tuple[str, Optional[str]]:
    """
    Determine the interval parameter based on provided arguments.
    Returns (interval, error_message)
    """
    # Convert string parameters to int if needed (MCP framework passes as strings)
    if recent_days is not None:
        if isinstance(recent_days, str):
            try:
                recent_days = int(recent_days)
            except (ValueError, TypeError):
                return "", "recent_days must be a valid integer"
        elif not isinstance(recent_days, int):
            try:
                recent_days = int(recent_days)
            except (ValueError, TypeError):
                return "", "recent_days must be a valid integer"
    
    if recent_count is not None:
        if isinstance(recent_count, str):
            try:
                recent_count = int(recent_count)
            except (ValueError, TypeError):
                return "", "recent_count must be a valid integer"
        elif not isinstance(recent_count, int):
            try:
                recent_count = int(recent_count)
            except (ValueError, TypeError):
                return "", "recent_count must be a valid integer"
    
    # Determine interval parameter
    if start_date and end_date:
        if not (_validate_date_format(start_date) and _validate_date_format(end_date)):
            return "", "Both dates must be in YYYY-MM-DD format"
        
        # Validate date order
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                return "", "Start date must be before or equal to end date"
        except ValueError:
            return "", "Invalid date format"
        
        return _format_date_range(start_date, end_date), None
    elif recent_days:
        if recent_days <= 0:
            return "", "recent_days must be a positive integer"
        # Calculate date range for recent days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=recent_days)).strftime("%Y-%m-%d")
        return _format_date_range(start_date, end_date), None
    elif recent_count:
        if recent_count <= 0:
            return "", "recent_count must be a positive integer"
        # For recent_count, we need to use date range format
        # Get papers from last 30 days and limit results
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        return _format_date_range(start_date, end_date), None
    else:
        # Default to last 30 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        return _format_date_range(start_date, end_date), None


@mcp.tool()
def search_papers(server: Literal["biorxiv", "medrxiv"] = "biorxiv",
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 recent_days: Optional[Union[int, str]] = None,
                 recent_count: Optional[Union[int, str]] = None,
                 category: Optional[str] = None,
                 cursor: int = 0,
                 max_results: int = 100) -> Dict:
    """
    Search for papers on bioRxiv or medRxiv.
    
    Args:
        server: Either "biorxiv" or "medrxiv"
        start_date: Start date in YYYY-MM-DD format (for date range search)
        end_date: End date in YYYY-MM-DD format (for date range search)
        recent_days: Number of recent days to search (e.g., 7 for last week)
        recent_count: Number of most recent papers to retrieve
        category: Subject category filter (e.g., "cell biology", "microbiology")
        cursor: Starting position for pagination (0-based)
        max_results: Maximum number of results per page (up to 100)
        
    Returns:
        Dict with papers, messages, and pagination info
    """
    # Validate server parameter
    if server not in ["biorxiv", "medrxiv"]:
        return {"error": "Server must be either 'biorxiv' or 'medrxiv'"}
    
    # Determine interval parameter
    interval, error = _determine_interval(start_date, end_date, recent_days, recent_count)
    if error:
        return {"error": error}
    
    # Limit cursor to reasonable pagination
    cursor = max(0, min(cursor, 9900))  # API typically limits to ~10k results
    
    # Build URL and make request
    url = _build_details_url(server, interval, cursor, category)
    result = _query_biorxiv(url)
    
    # Check for API errors
    if "error" in result:
        return result
    
    # Add search metadata
    result["search_params"] = {
        "server": server,
        "interval": interval,
        "category": category,
        "cursor": cursor,
        "url": url
    }
    
    return result

@mcp.tool()
def get_paper_by_doi(doi: str, server: Literal["biorxiv", "medrxiv"] = "biorxiv") -> Dict:
    """
    Get detailed information for a specific paper by DOI.
    
    Args:
        doi: The DOI of the paper (e.g., "10.1101/2023.01.01.123456")
        server: Either "biorxiv" or "medrxiv"
        
    Returns:
        Dict with paper details or error message
    """
    if not doi:
        return {"error": "DOI parameter is required"}
    
    if server not in ["biorxiv", "medrxiv"]:
        return {"error": "Server must be either 'biorxiv' or 'medrxiv'"}
    
    url = _build_doi_url(server, doi)
    result = _query_biorxiv(url)
    
    if "error" in result:
        return result
    
    result["search_params"] = {
        "doi": doi,
        "server": server,
        "url": url
    }
    
    return result

@mcp.tool()
def get_published_papers(server: Literal["biorxiv", "medrxiv"] = "biorxiv",
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        recent_days: Optional[Union[int, str]] = None,
                        recent_count: Optional[Union[int, str]] = None,
                        cursor: int = 0) -> Dict:
    """
    Get information about preprints that have been published in peer-reviewed journals.
    
    Args:
        server: Either "biorxiv" or "medrxiv"
        start_date: Start date in YYYY-MM-DD format (for date range search)
        end_date: End date in YYYY-MM-DD format (for date range search)
        recent_days: Number of recent days to search (e.g., 30 for last month)
        recent_count: Number of most recent published papers to retrieve
        cursor: Starting position for pagination (0-based)
        
    Returns:
        Dict containing:
        - messages: List of status messages
        - cursor: Current pagination position
        - count: Number of published papers found
        - total: Total number of published papers in date range
        - published: List of published paper objects with fields:
          * doi: The preprint DOI
          * published_doi: The published journal DOI
          * published_date: Date of publication
          * published_journal: Journal name
          * published_url: Link to published version
        - search_params: Search parameters used
        
    Examples:
        - get_published_papers("biorxiv", recent_days=7)
        - get_published_papers("medrxiv", start_date="2024-01-01", end_date="2024-12-31")
        - get_published_papers("biorxiv", recent_count=50)
        
    Note:
        - Tracks preprints that have been accepted by peer-reviewed journals
        - Useful for finding which preprints have been validated by the scientific community
        - Date parameters work the same as search_papers function
        - Returns both preprint and published version information
        - Limited to papers published in the specified date range
    """
    if server not in ["biorxiv", "medrxiv"]:
        return {"error": "Server must be either 'biorxiv' or 'medrxiv'"}
    
    # Determine interval parameter
    interval, error = _determine_interval(start_date, end_date, recent_days, recent_count)
    if error:
        return {"error": error}
    
    cursor = max(0, cursor)
    
    url = _build_pubs_url(server, interval, cursor)
    result = _query_biorxiv(url)
    
    if "error" in result:
        return result
    
    result["search_params"] = {
        "server": server,
        "interval": interval,
        "cursor": cursor,
        "url": url
    }
    
    return result

@mcp.tool()
def search_by_funder(funder_ror_id: str,
                    server: Literal["biorxiv", "medrxiv"] = "biorxiv",
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    recent_days: Optional[Union[int, str]] = None,
                    recent_count: Optional[Union[int, str]] = None,
                    category: Optional[str] = None,
                    cursor: int = 0) -> Dict:
    """
    Search for papers by funder using ROR ID.
    
    Args:
        funder_ror_id: 9-character ROR ID (e.g., "02mhbdp94" for European Commission)
        server: Either "biorxiv" or "medrxiv"
        start_date: Start date (must be 2025-04-10 or later)
        end_date: End date in YYYY-MM-DD format
        recent_days: Number of recent days to search
        recent_count: Number of most recent papers
        category: Subject category filter
        cursor: Starting position for pagination
        
    Returns:
        Dict with funder-filtered papers
    """
    # Validate required parameters
    if not funder_ror_id:
        return {"error": "funder_ror_id parameter is required"}
    
    if len(funder_ror_id) != 9:
        return {"error": "Funder ROR ID must be exactly 9 characters"}
    
    if server not in ["biorxiv", "medrxiv"]:
        return {"error": "Server must be either 'biorxiv' or 'medrxiv'"}
    
    # Determine interval parameter
    interval, error = _determine_interval(start_date, end_date, recent_days, recent_count)
    if error:
        return {"error": error}
    
    # Validate minimum start date for funder endpoint if using date range
    if start_date:
        min_date = datetime(2025, 4, 10)
        try:
            if datetime.strptime(start_date, "%Y-%m-%d") < min_date:
                return {"error": "Start date must be 2025-04-10 or later for funder searches"}
        except ValueError:
            return {"error": "Invalid start_date format"}
    
    cursor = max(0, cursor)
    
    url = _build_funder_url(server, interval, funder_ror_id, cursor, category)
    result = _query_biorxiv(url)
    
    if "error" in result:
        return result
    
    result["search_params"] = {
        "server": server,
        "funder_ror_id": funder_ror_id,
        "interval": interval,
        "category": category,
        "cursor": cursor,
        "url": url
    }
    
    return result

@mcp.tool()
def get_content_summary(interval: Literal["m", "y"] = "m") -> Dict:
    """
    Get content summary statistics for bioRxiv preprint server.
    
    Args:
        interval: Time interval for statistics
                 - "m": Monthly statistics (default)
                 - "y": Yearly statistics
                 
    Returns:
        Dict containing:
        - messages: List of status messages
        - summary: Summary statistics object with fields:
          * total_papers: Total number of papers in period
          * new_papers: Number of new papers added
          * categories: Breakdown by subject category
          * authors: Author statistics
          * institutions: Institution statistics
          * countries: Geographic distribution
        - search_params: Query parameters used
        
    Examples:
        - get_content_summary("m")  # Monthly stats
        - get_content_summary("y")  # Yearly stats
        
    Note:
        - Provides high-level statistics about bioRxiv content
        - Monthly stats show current month activity
        - Yearly stats show calendar year totals
        - Useful for understanding preprint submission trends
        - Includes geographic and institutional breakdowns
        - Only covers bioRxiv (not medRxiv)
    """
    if interval not in ["m", "y"]:
        return {"error": "Interval must be either 'm' (monthly) or 'y' (yearly)"}
    
    url = f"{BASE_URL}/sum/{interval}"
    result = _query_biorxiv(url)
    
    if "error" in result:
        return result
    
    result["search_params"] = {
        "interval": interval,
        "url": url
    }
    
    return result

@mcp.tool()
def get_usage_statistics(interval: Literal["m", "y"] = "m") -> Dict:
    """
    Get usage statistics for bioRxiv (views, downloads).
    
    Args:
        interval: "m" for monthly or "y" for yearly statistics
        
    Returns:
        Dict with usage statistics
    """
    if interval not in ["m", "y"]:
        return {"error": "Interval must be either 'm' (monthly) or 'y' (yearly)"}
    
    url = f"{BASE_URL}/usage/{interval}"
    result = _query_biorxiv(url)
    
    if "error" in result:
        return result
    
    result["search_params"] = {
        "interval": interval,
        "url": url
    }
    
    return result

@mcp.tool()
def download_pdf(doi: str, dest_dir: str = "downloads") -> Dict:
    """
    Download a paper's PDF from bioRxiv or medRxiv and save it locally.
    
    Args:
        doi: The DOI of the paper. Can be:
             - Full DOI: "10.1101/2023.01.01.123456"
             - Short DOI: "2023.01.01.123456"
             - Date format: "2023.01.01.123456"
        dest_dir: Local directory path for storing PDFs.
                  Directory will be created if it doesn't exist.
                  Default: "downloads"
                  
    Returns:
        Dict containing:
        - doi: The DOI used for download
        - pdf_url: The successful PDF URL
        - local_path: Full path to the saved PDF file
        - size_bytes: Size of the downloaded file in bytes
        
        Or error dict with:
        - error: Error message describing the failure
        - doi: The DOI that failed
        - attempted_urls: List of URLs that were tried
        
    Examples:
        - download_pdf("2023.01.01.123456")
        - download_pdf("10.1101/2023.01.01.123456", "papers/biology")
        - download_pdf("2023.12.25.567890", "research/medrxiv")
        
    Note:
        - Automatically tries multiple URL formats for maximum compatibility
        - Attempts structured URLs for date-formatted DOIs
        - Falls back to standard bioRxiv/medRxiv URLs
        - Uses streaming download for large files
        - 60-second timeout for download requests
        - Returns error if all URL attempts fail
        - File is saved as "{clean_doi}.pdf" in dest_dir
    """
    if not doi:
        return {"error": "DOI parameter is required"}
    
    # Clean DOI - remove "10.1101/" prefix if present
    clean_doi = doi.replace("10.1101/", "")
    
    # Try multiple PDF URL formats
    pdf_urls = [
        f"https://www.biorxiv.org/content/10.1101/{clean_doi}.full.pdf",
        f"https://www.medrxiv.org/content/10.1101/{clean_doi}.full.pdf"
    ]
    
    # If DOI has date format, try the structured URL
    if len(clean_doi.split('.')) >= 3:
        try:
            parts = clean_doi.split('.')
            year = parts[0]
            month = parts[1]
            day = parts[2]
            structured_url = f"https://www.biorxiv.org/content/biorxiv/early/{year}/{month.zfill(2)}/{day.zfill(2)}/{clean_doi}.full.pdf"
            pdf_urls.insert(0, structured_url)
        except (IndexError, ValueError):
            pass  # Fall back to simpler URLs
    
    # Ensure target directory exists
    dest_path = pathlib.Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    file_path = dest_path / f"{clean_doi}.pdf"
    
    # Try each URL until one works
    for pdf_url in pdf_urls:
        try:
            with requests.get(pdf_url, headers=HEADERS, stream=True, timeout=60) as r:
                if r.status_code == 200:
                    # Write the file in chunks
                    with open(file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    return {
                        "doi": doi,
                        "pdf_url": pdf_url,
                        "local_path": str(file_path.resolve()),
                        "size_bytes": file_path.stat().st_size
                    }
        except requests.RequestException:
            continue  # Try next URL
    
    return {
        "error": f"Failed to download PDF from any of the attempted URLs",
        "doi": doi,
        "attempted_urls": pdf_urls
    }

if __name__ == "__main__":
    mcp.run() 