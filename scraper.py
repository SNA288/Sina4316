# Scraper.py v1.2.6
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

# Common headers to mimic browser behavior
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
}

def search_movies(query, page=1):
    logging.info(f"Searching for movies with query: {query}, page: {page}")
    base_url = 'https://www.f2miv.ir/'
    search_url = f"{base_url}page/{page}/?controller=search-movie&s={query}"  # Adjusted to include pagination

    
        response = requests.get(search_url, headers=HEADERS)  # Added headers
        response.raise_for_status()  # Will raise an error if status code is not 200
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        # Updated CSS selector for fetching movie links
        for item in soup.select('div.m_info h2.movie-title a'):
            name = item.get_text(strip=True)
            link = item.get('href')
            if query.lower() in name.lower():
                results.append((name, link))

        return results

def scrape_download_links(movie_url):
        response = requests.get(movie_url, headers=HEADERS)  # Added headers
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        download_links = defaultdict(list)
        for link in soup.select('a[href]'):
            href = link.get('href').lower()  # Normalize to lowercase

            if 'dubbed' in href:  # Check for dubbed versions, case-insensitive
                if '1080p' in href:
                    if 'x265' in href:
                        download_links['1080p x265 Dubbed'].append(link.get('href'))
                    else:
                        download_links['1080p H.264 Dubbed'].append(link.get('href'))
                elif '720p' in href:
                    if 'x265' in href:
                        download_links['720p x265 Dubbed'].append(link.get('href'))
                    else:
                        download_links['720p H.264 Dubbed'].append(link.get('href'))
            else:  # For non-dubbed versions
                if '1080p' in href:
                    if 'x265' in href:
                        download_links['1080p x265'].append(link.get('href'))
                    else:
                        download_links['1080p H.264'].append(link.get('href'))
                elif '720p' in href:
                    if 'x265' in href:
                        download_links['720p x265'].append(link.get('href'))
                    else:
                        download_links['720p H.264'].append(link.get('href'))

        return download_links

