import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
START_URL = BASE_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ScrapingAssignment/1.0)"
}

logger = logging.getLogger(__name__)


class QuotesScraper:
    """Scraper for Quotes to Scrape."""

    def __init__(self, start_url=START_URL, timeout=10):
        self.start_url = start_url
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_page(self, url):
        """Download a page and return a BeautifulSoup object."""

        try:
            response = self.session.get(
                url,
                timeout=self.timeout
            )

            response.raise_for_status()

            response.encoding = response.apparent_encoding

            return BeautifulSoup(
                response.text,
                "html.parser"
            )

        except requests.RequestException as exc:
            logger.error(
                "Failed to fetch %s: %s",
                url,
                exc
            )

            return None

    @staticmethod
    def clean_text(value):
        """Normalize whitespace in scraped text."""

        if not value:
            return None

        return " ".join(value.split()).strip()

    def scrape_page(self, page_url):
        """Scrape all quotes from one page."""

        soup = self.fetch_page(page_url)

        if soup is None:
            return [], None

        quote_elements = soup.select(
            "div.quote"
        )

        records = []

        for quote in quote_elements:

            text_element = quote.select_one(
                "span.text"
            )

            author_element = quote.select_one(
                "small.author"
            )

            tag_elements = quote.select(
                "a.tag"
            )

            if not text_element:
                logger.warning(
                    "Skipping quote because text "
                    "is missing: %s",
                    page_url
                )

                continue

            quote_text = self.clean_text(
                text_element.get_text()
            )

            author = (
                self.clean_text(
                    author_element.get_text()
                )
                if author_element
                else None
            )

            tags = [
                self.clean_text(
                    tag.get_text()
                )
                for tag in tag_elements
                if self.clean_text(
                    tag.get_text()
                )
            ]

            record = {
                "source": "Quotes to Scrape",
                "source_url": page_url,
                "name_or_title": quote_text,
                "category": None,
                "price": None,
                "rating": None,
                "author": author,
                "tags": tags,
                "description": None,
                "scraped_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            records.append(record)

        next_link = soup.select_one(
            "li.next a"
        )

        next_url = (
            urljoin(
                page_url,
                next_link.get("href")
            )
            if next_link
            else None
        )

        return records, next_url

    def scrape(self, max_pages=None):
        """
        Scrape quotes from all available pages.

        max_pages is useful during testing.

        If max_pages is None, all available pages
        are scraped.
        """

        all_records = []

        current_url = self.start_url
        page_number = 1

        while current_url:

            if (
                max_pages is not None
                and page_number > max_pages
            ):
                break

            logger.info(
                "Scraping quotes page %d: %s",
                page_number,
                current_url
            )

            page_records, next_url = (
                self.scrape_page(
                    current_url
                )
            )

            logger.info(
                "Found %d quotes on page %d",
                len(page_records),
                page_number
            )

            all_records.extend(
                page_records
            )

            current_url = next_url
            page_number += 1

        logger.info(
            "Finished scraping. Total quotes: %d",
            len(all_records)
        )

        return all_records