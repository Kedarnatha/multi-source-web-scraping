import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ScrapingAssignment/1.0)"
}

logger = logging.getLogger(__name__)


class BooksScraper:
    """Scraper for Books to Scrape."""

    def __init__(self, start_url=START_URL, timeout=10):
        self.start_url = start_url
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_page(self, url, max_retries=3):
        """Download a page with retry handling."""

        for attempt in range(1, max_retries + 1):
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
                logger.warning(
                    "Request failed for %s "
                    "(attempt %d/%d): %s",
                    url,
                    attempt,
                    max_retries,
                    exc
                )

                if attempt < max_retries:
                    wait_seconds = 2 ** (attempt - 1)
                    logger.info(
                        "Retrying in %d seconds...",
                        wait_seconds
                    )
                    time.sleep(wait_seconds)
                else:
                    logger.error(
                        "Failed to fetch %s after %d attempts",
                        url,
                        max_retries
                    )

        return None

    @staticmethod
    def clean_text(value):
        """Normalize whitespace in scraped text."""

        if not value:
            return None

        return " ".join(value.split()).strip()

    @staticmethod
    def parse_price(price_text):
        """Convert a price string such as '£51.77' to a float."""

        if not price_text:
            return None

        try:
            cleaned = (
                price_text
                .replace("Â£", "")
                .replace("£", "")
                .strip()
            )

            return float(cleaned)

        except (ValueError, AttributeError):
            logger.warning(
                "Could not parse price: %r",
                price_text
            )

            return None


    @staticmethod
    def parse_rating(product):
        """Convert star-rating text into an integer from 1 to 5."""

        rating_element = product.select_one(
            "p.star-rating"
        )

        if not rating_element:
            return None

        rating_classes = rating_element.get(
            "class",
            []
        )

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        for class_name, rating_value in rating_map.items():

            if class_name in rating_classes:
                return rating_value

        logger.warning(
            "Unknown rating classes: %s",
            rating_classes
        )

        return None

    def scrape_product(self, product_url):
        """Scrape detailed information from an individual book page."""

        soup = self.fetch_page(product_url)

        if soup is None:
            return None

        title_element = soup.select_one(
            "div.product_main h1"
        )

        price_element = soup.select_one(
            "div.product_main p.price_color"
        )

        description_element = soup.select_one(
            "#product_description + p"
        )
        category_element = soup.select_one(
             "ul.breadcrumb li:nth-of-type(3) a"
        )

        title = (
            self.clean_text(
                title_element.get_text()
            )
            if title_element
            else None
        )

        price = (
            self.parse_price(
                price_element.get_text()
            )
            if price_element
            else None
        )

        description = (
            self.clean_text(
                description_element.get_text()
            )
            if description_element
            else None
        )
        category = (
            self.clean_text(
                category_element.get_text()
            )
            if category_element
            else None
        )

        if not title:
            logger.warning(
                "Missing book title: %s",
                product_url
            )

            return None

        return {
            "source": "Books to Scrape",
            "source_url": product_url,
            "name_or_title": title,
            "category": category,
            "price": price,
            "rating": None,
            "author": None,
            "tags": [],
            "description": description,
            "scraped_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def scrape_catalogue_page(self, page_url):
        """Scrape all books from one catalogue page."""

        soup = self.fetch_page(page_url)

        if soup is None:
            return [], None

        products = soup.select(
            "article.product_pod"
        )

        records = []

        for product in products:

            title_element = product.select_one(
                "h3 a"
            )

            price_element = product.select_one(
                "p.price_color"
            )

            if not title_element:
                logger.warning(
                    "Skipping product because title "
                    "link is missing: %s",
                    page_url
                )

                continue

            product_url = urljoin(
                page_url,
                title_element.get("href", "")
            )

            title = self.clean_text(
                title_element.get("title")
            )

            price = (
                self.parse_price(
                    price_element.get_text()
                )
                if price_element
                else None
            )

            rating = self.parse_rating(
                product
            )

            record = {
                "source": "Books to Scrape",
                "source_url": product_url,
                "name_or_title": title,
                "category": None,
                "price": price,
                "rating": rating,
                "author": None,
                "tags": [],
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
        Scrape books from all catalogue pages.

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
                "Scraping catalogue page %d: %s",
                page_number,
                current_url
            )

            page_records, next_url = (
                self.scrape_catalogue_page(
                    current_url
                )
            )

            logger.info(
                "Found %d books on page %d",
                len(page_records),
                page_number
            )

            for record in page_records:

                detailed_record = (
                    self.scrape_product(
                        record["source_url"]
                    )
                )

                if detailed_record:

                    detailed_record["rating"] = (
                        record["rating"]
                    )

                    all_records.append(
                        detailed_record
                    )

                else:
                    # Keep the catalogue record
                    # if the detail page fails.
                    all_records.append(record)

            current_url = next_url
            page_number += 1

        logger.info(
            "Finished scraping. Total books: %d",
            len(all_records)
        )

        return all_records