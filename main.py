import json
import logging
import os
import time
from datetime import datetime, timezone

from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.processor import DataProcessor


OUTPUT_DIR = "output"
LOG_DIR = "logs"

CSV_PATH = os.path.join(
    OUTPUT_DIR,
    "final_dataset.csv"
)

JSON_PATH = os.path.join(
    OUTPUT_DIR,
    "summary_report.json"
)

LOG_PATH = os.path.join(
    LOG_DIR,
    "scraper.log"
)


def setup_logging():
    """Configure console and file logging."""

    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                LOG_PATH,
                encoding="utf-8"
            ),
            logging.StreamHandler(),
        ],
    )


def main():
    """Run the complete scraping and processing pipeline."""

    setup_logging()

    logger = logging.getLogger(__name__)

    start_time = time.time()

    execution_started_at = datetime.now(
        timezone.utc
    ).isoformat()

    logger.info(
        "Starting multi-source scraping pipeline"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --------------------------------------------------
    # 1. Scrape Books
    # --------------------------------------------------

    books_scraper = BooksScraper()

    logger.info(
        "Starting Books to Scrape"
    )

    books_records = books_scraper.scrape()

    logger.info(
        "Books scraped: %d",
        len(books_records)
    )

    # --------------------------------------------------
    # 2. Scrape Quotes
    # --------------------------------------------------

    quotes_scraper = QuotesScraper()

    logger.info(
        "Starting Quotes to Scrape"
    )

    quotes_records = quotes_scraper.scrape()

    logger.info(
        "Quotes scraped: %d",
        len(quotes_records)
    )

    # --------------------------------------------------
    # 3. Combine source records
    # --------------------------------------------------

    all_records = (
        books_records +
        quotes_records
    )

    logger.info(
        "Total raw records: %d",
        len(all_records)
    )

    # --------------------------------------------------
    # 4. Process records
    # --------------------------------------------------

    processor = DataProcessor()

    cleaned_records = processor.clean_records(
        all_records
    )

    valid_records, rejected_records = (
        processor.validate_records(
            cleaned_records
        )
    )

    unique_records, duplicate_records = (
        processor.deduplicate_records(
            valid_records
        )
    )

    # --------------------------------------------------
    # 5. Create final DataFrame
    # --------------------------------------------------

    dataframe = processor.to_dataframe(
        unique_records
    )

    dataframe.to_csv(
        CSV_PATH,
        index=False,
        encoding="utf-8"
    )

    logger.info(
        "Final CSV written to %s",
        CSV_PATH
    )

    # --------------------------------------------------
    # 6. Calculate source metrics
    # --------------------------------------------------

    source_metrics = {}

    for source in [
        "Books to Scrape",
        "Quotes to Scrape",
    ]:

        raw_count = sum(
            1
            for record in all_records
            if record.get("source") == source
        )

        cleaned_count = sum(
            1
            for record in cleaned_records
            if record.get("source") == source
        )

        rejected_count = sum(
            1
            for item in rejected_records
            if item["record"].get("source") == source
        )

        duplicate_count = sum(
            1
            for record in duplicate_records
            if record.get("source") == source
        )

        final_count = sum(
            1
            for record in unique_records
            if record.get("source") == source
        )

        source_metrics[source] = {
            "raw_records": raw_count,
            "after_cleaning": cleaned_count,
            "rejected_records": rejected_count,
            "duplicates_removed": duplicate_count,
            "final_records": final_count,
        }

    # --------------------------------------------------
    # 7. Create summary report
    # --------------------------------------------------

    execution_time = round(
        time.time() - start_time,
        2
    )

    summary = {
        "execution_started_at": execution_started_at,
        "execution_time_seconds": execution_time,

        "total_raw_records": len(all_records),

        "total_after_cleaning": len(
            cleaned_records
        ),

        "total_rejected_records": len(
            rejected_records
        ),

        "total_duplicates_removed": len(
            duplicate_records
        ),

        "final_record_count": len(
            unique_records
        ),

        "sources": source_metrics,
    }

    with open(
        JSON_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "Summary report written to %s",
        JSON_PATH
    )

    logger.info(
        "Pipeline completed successfully"
    )

    print()
    print("=" * 60)
    print("SCRAPING PIPELINE COMPLETED")
    print("=" * 60)
    print(
        f"Raw records: {len(all_records)}"
    )
    print(
        f"Cleaned records: {len(cleaned_records)}"
    )
    print(
        f"Rejected records: {len(rejected_records)}"
    )
    print(
        f"Duplicates removed: {len(duplicate_records)}"
    )
    print(
        f"Final records: {len(unique_records)}"
    )
    print(
        f"Execution time: {execution_time} seconds"
    )
    print()
    print(
        f"CSV: {CSV_PATH}"
    )
    print(
        f"JSON: {JSON_PATH}"
    )
    print(
        f"Log: {LOG_PATH}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()