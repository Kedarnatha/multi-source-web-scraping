import logging

from scrapers.books_scraper import BooksScraper


logging.basicConfig(
    level=logging.INFO
)


scraper = BooksScraper()

books = scraper.scrape(
    max_pages=2
)

print()
print("=" * 60)
print(f"Books scraped: {len(books)}")
print("=" * 60)

for book in books[:3]:
    print(book)
    print()