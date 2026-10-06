import logging
import re
from urllib.parse import urlparse

import pandas as pd


logger = logging.getLogger(__name__)


class DataProcessor:
    """Clean, validate, deduplicate, and consolidate scraped records."""

    REQUIRED_FIELDS = [
        "source",
        "source_url",
        "name_or_title",
        "scraped_at",
    ]

    def clean_text(self, value):
        """Normalize whitespace and return None for empty values."""

        if value is None:
            return None

        if not isinstance(value, str):
            return value

        cleaned = " ".join(value.split()).strip()

        return cleaned if cleaned else None

    def clean_price(self, value):
        """Convert price values to numeric values."""

        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            cleaned = (
                value
                .replace("Â£", "")
                .replace("£", "")
                .replace(",", "")
                .strip()
            )

            try:
                return float(cleaned)
            except ValueError:
                logger.warning(
                    "Invalid price value: %r",
                    value
                )
                return None

        return None

    def clean_rating(self, value):
        """Convert ratings to a standardized numeric value."""

        if value is None:
            return None

        if isinstance(value, (int, float)):
            rating = int(value)

            if 1 <= rating <= 5:
                return rating

            return None

        if isinstance(value, str):
            rating_map = {
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5,
            }

            cleaned = value.strip().lower()

            if cleaned.isdigit():
                rating = int(cleaned)

                if 1 <= rating <= 5:
                    return rating

            return rating_map.get(cleaned)

        return None

    def clean_tags(self, value):
        """Normalize tags into a clean list."""

        if value is None:
            return []

        if isinstance(value, list):
            cleaned_tags = []

            for tag in value:
                cleaned = self.clean_text(tag)

                if cleaned:
                    cleaned_tags.append(cleaned)

            return cleaned_tags

        if isinstance(value, str):
            return [
                tag.strip()
                for tag in value.split(",")
                if tag.strip()
            ]

        return []

    def clean_record(self, record):
        """Clean one scraped record."""

        cleaned = record.copy()

        text_fields = [
            "source",
            "source_url",
            "name_or_title",
            "category",
            "author",
            "description",
            "scraped_at",
        ]

        for field in text_fields:
            if field in cleaned:
                cleaned[field] = self.clean_text(
                    cleaned[field]
                )

        cleaned["price"] = self.clean_price(
            cleaned.get("price")
        )

        cleaned["rating"] = self.clean_rating(
            cleaned.get("rating")
        )

        cleaned["tags"] = self.clean_tags(
            cleaned.get("tags")
        )

        return cleaned

    def clean_records(self, records):
        """Clean all records."""

        cleaned_records = []

        for record in records:
            try:
                cleaned_records.append(
                    self.clean_record(record)
                )
            except Exception as exc:
                logger.error(
                    "Failed to clean record: %s",
                    exc
                )

        logger.info(
            "Cleaned %d records",
            len(cleaned_records)
        )

        return cleaned_records

    def validate_record(self, record):
        """Validate one record against the common schema."""

        for field in self.REQUIRED_FIELDS:
            if not record.get(field):
                return False, f"Missing required field: {field}"

        if record.get("price") is not None:
            if not isinstance(
                record["price"],
                (int, float)
            ):
                return False, "Price must be numeric"

            if record["price"] < 0:
                return False, "Price cannot be negative"

        if record.get("rating") is not None:
            if not isinstance(
                record["rating"],
                int
            ):
                return False, "Rating must be an integer"

            if not 1 <= record["rating"] <= 5:
                return False, "Rating must be between 1 and 5"

        source_url = record.get("source_url")

        if source_url:
            parsed_url = urlparse(source_url)

            if parsed_url.scheme not in (
                "http",
                "https",
            ) or not parsed_url.netloc:
                return False, "Invalid source URL"

        return True, None

    def validate_records(self, records):
        """Validate all records and separate rejected records."""

        valid_records = []
        rejected_records = []

        for record in records:
            is_valid, reason = self.validate_record(
                record
            )

            if is_valid:
                valid_records.append(record)
            else:
                rejected_records.append(
                    {
                        "record": record,
                        "reason": reason,
                    }
                )

                logger.warning(
                    "Rejected record: %s",
                    reason
                )

        logger.info(
            "Validation complete: %d valid, %d rejected",
            len(valid_records),
            len(rejected_records),
        )

        return valid_records, rejected_records

    @staticmethod
    def normalize_for_deduplication(value):
        """Normalize text for duplicate detection."""

        if value is None:
            return ""

        value = str(value).lower().strip()

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        return value

    def deduplicate_records(self, records):
        """
        Remove duplicate records.

        The deduplication key uses source + title/name + author.
        """

        unique_records = []
        duplicate_records = []
        seen_keys = set()

        for record in records:

            key = (
                self.normalize_for_deduplication(
                    record.get("source")
                ),
                self.normalize_for_deduplication(
                    record.get("name_or_title")
                ),
                self.normalize_for_deduplication(
                    record.get("author")
                ),
            )

            if key in seen_keys:
                duplicate_records.append(record)

                logger.info(
                    "Duplicate record removed: %s",
                    record.get("name_or_title")
                )

                continue

            seen_keys.add(key)
            unique_records.append(record)

        logger.info(
            "Deduplication complete: %d unique, %d duplicates",
            len(unique_records),
            len(duplicate_records),
        )

        return unique_records, duplicate_records

    def to_dataframe(self, records):
        """Convert records to a pandas DataFrame."""

        columns = [
            "source",
            "source_url",
            "name_or_title",
            "category",
            "price",
            "rating",
            "author",
            "tags",
            "description",
            "scraped_at",
        ]

        dataframe = pd.DataFrame(
            records,
            columns=columns
        )

        return dataframe