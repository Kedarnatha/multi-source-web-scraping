from processing.processor import DataProcessor


def test_clean_price():
    processor = DataProcessor()

    assert processor.clean_price("£51.77") == 51.77
    assert processor.clean_price("Â£51.77") == 51.77
    assert processor.clean_price("1,234.50") == 1234.50
    assert processor.clean_price(None) is None


def test_clean_rating():
    processor = DataProcessor()

    assert processor.clean_rating("Five") == 5
    assert processor.clean_rating("three") == 3
    assert processor.clean_rating("4") == 4
    assert processor.clean_rating(5) == 5
    assert processor.clean_rating("7") is None


def test_clean_text():
    processor = DataProcessor()

    assert processor.clean_text("  Hello    world  ") == "Hello world"
    assert processor.clean_text("") is None
    assert processor.clean_text(None) is None


def test_validate_record():
    processor = DataProcessor()

    valid_record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": "Test Book",
        "scraped_at": "2026-10-06T00:00:00+00:00",
        "price": 10.99,
        "rating": 4,
    }

    is_valid, reason = processor.validate_record(valid_record)

    assert is_valid is True
    assert reason is None


def test_invalid_price():
    processor = DataProcessor()

    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": "Test Book",
        "scraped_at": "2026-10-06T00:00:00+00:00",
        "price": -10,
        "rating": 4,
    }

    is_valid, reason = processor.validate_record(record)

    assert is_valid is False
    assert reason == "Price cannot be negative"


def test_deduplication():
    processor = DataProcessor()

    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": "Test Book",
            "author": None,
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "  TEST   BOOK ",
            "author": None,
        },
    ]

    unique_records, duplicate_records = (
        processor.deduplicate_records(records)
    )

    assert len(unique_records) == 1
    assert len(duplicate_records) == 1