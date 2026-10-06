import logging

from scrapers.quotes_scraper import QuotesScraper


logging.basicConfig(
    level=logging.INFO
)


scraper = QuotesScraper()

quotes = scraper.scrape(
    max_pages=2
)

print()
print("=" * 60)
print(f"Quotes scraped: {len(quotes)}")
print("=" * 60)

for quote in quotes[:3]:
    print(quote)
    print()
