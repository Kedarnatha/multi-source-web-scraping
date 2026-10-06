# Multi-Source Web Scraping & Data Consolidation

## 1. Project Overview

This project implements a Python-based multi-source web scraping pipeline that extracts data from two websites, normalizes the results into a common schema, cleans and validates the records, removes duplicates, and generates consolidated CSV and JSON outputs.

The two sources are:

- **Books to Scrape** — book catalogue data
- **Quotes to Scrape** — quotes, authors, and tags

The implementation uses separate scraper modules for each source and a shared processing layer for cleaning, validation, deduplication, and consolidation.

---

## 2. Source Exploration

### Books to Scrape

URL: https://books.toscrape.com/

Books to Scrape provides a paginated catalogue of books.

The scraper dynamically follows the catalogue's `Next` pagination link until no additional page is available. It does not rely on a hard-coded number of pages.

For each book, the scraper extracts information from the catalogue and individual product pages, including:

- Book title
- Product URL
- Category
- Price
- Rating
- Description

The Books scraper also handles missing HTML elements without terminating the complete scraping process.

### Quotes to Scrape

URL: https://quotes.toscrape.com/

Quotes to Scrape provides a paginated collection of quotes.

The scraper dynamically follows the `Next` pagination link until there are no additional pages.

Each quote can contain:

- Quote text
- Author
- Tags

Fields that are not provided by the source are represented as `None` or an empty collection rather than being invented.

---

## 3. Technology Stack

The project uses:

- **Python** — application and scraping logic
- **Requests** — HTTP requests
- **BeautifulSoup** — HTML parsing
- **Pandas** — tabular processing and CSV generation
- **Pytest** — automated testing

The target websites expose the required information through server-rendered HTML, so browser automation is not required.

---

## 4. Project Structure

```text
scraping_assignment/
│
├── scrapers/
│   ├── __init__.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
│
├── processing/
│   ├── __init__.py
│   └── processor.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_books_scraper.py
│   ├── test_quotes_scraper.py
│   └── test_processor.py
│
├── output/
│   ├── final_dataset.csv
│   └── summary_report.json
│
├── logs/
│   └── scraper.log
│
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

---

## 5. Common Data Model

Both sources are normalized into the following common schema:

| Field | Description |
|---|---|
| `source` | Name of the source website |
| `source_url` | Original URL associated with the scraped record |
| `name_or_title` | Main title or identifying text |
| `category` | Category when provided |
| `price` | Numeric price when provided |
| `rating` | Standardized rating when provided |
| `author` | Author when provided |
| `tags` | Tags associated with the record |
| `description` | Description when provided |
| `scraped_at` | UTC timestamp when the record was scraped |

### Books Source Mapping

| Common Field | Books Data |
|---|---|
| `source` | Books to Scrape |
| `source_url` | Product URL |
| `name_or_title` | Book title |
| `category` | Book category |
| `price` | Book price |
| `rating` | Star rating |
| `author` | `None` when not provided |
| `tags` | Empty list when not provided |
| `description` | Book description |
| `scraped_at` | Scraping timestamp |

### Quotes Source Mapping

| Common Field | Quotes Data |
|---|---|
| `source` | Quotes to Scrape |
| `source_url` | Quote page URL |
| `name_or_title` | Quote text |
| `category` | `None` |
| `price` | `None` |
| `rating` | `None` |
| `author` | Quote author |
| `tags` | Quote tags |
| `description` | `None` |
| `scraped_at` | Scraping timestamp |

---

## 6. Scraping and Pagination

Each source has its own scraper module:

- `scrapers/books_scraper.py`
- `scrapers/quotes_scraper.py`

Pagination is discovered dynamically from the HTML `Next` link.

The scrapers continue requesting pages until no next page is available.

The Books scraper follows product URLs when additional book-level fields are required.

---

## 7. Error Handling and Retries

The scrapers include error handling for request-related failures, including:

- Connection failures
- HTTP errors
- Request timeouts
- Failed page requests

Failed requests are retried up to three times.

Retry delays use exponential backoff:

```text
Attempt 1 → wait 1 second
Attempt 2 → wait 2 seconds
Attempt 3 → fail and log the error
```

Errors and warnings are written to:

```text
logs/scraper.log
```

A failed page does not cause the entire application to terminate unnecessarily.

Missing HTML elements are handled defensively and do not cause the complete scraper to crash.

---

## 8. Data Cleaning

Data cleaning is implemented separately from the source-specific scraping logic in:

```text
processing/processor.py
```

Cleaning includes:

- Whitespace normalization
- Text normalization
- Currency symbol removal
- Conversion of prices to numeric values
- Rating standardization
- Tag normalization
- Consistent missing-value handling

No values are invented when a source does not provide them.

---

## 9. Data Validation

Records are validated after cleaning.

Validation checks include:

- Required fields are present
- Price values are numeric when provided
- Price values are not negative
- Ratings are integers when provided
- Ratings are within the expected 1–5 range
- Source URLs use valid HTTP/HTTPS URL formats

Invalid records are rejected and recorded in the processing metrics rather than being silently included in the final dataset.

---

## 10. Deduplication

Duplicate detection is performed after validation.

The deduplication key uses:

- Source
- `name_or_title`
- Author

Values used for comparison are normalized by:

- Converting to lowercase
- Removing leading/trailing whitespace
- Normalizing repeated whitespace

This provides a repeatable deduplication strategy that is more robust than comparing raw strings directly.

The number of removed duplicate records is included in the summary report.

---

## 11. Processing Pipeline

The complete pipeline is:

1. Scrape Books to Scrape.
2. Scrape Quotes to Scrape.
3. Normalize both sources into the common data model.
4. Clean the extracted records.
5. Validate the cleaned records.
6. Remove duplicate records.
7. Consolidate valid records.
8. Generate the final CSV dataset.
9. Generate the JSON summary report.
10. Record execution information in the log file.

---

## 12. Output Files

### Final Dataset

```text
output/final_dataset.csv
```

Contains the consolidated records using the common schema.

### Summary Report

```text
output/summary_report.json
```

Contains:

- Execution start time
- Execution time
- Total raw records
- Records after cleaning
- Rejected records
- Duplicate records removed
- Final record count
- Per-source metrics

### Logs

```text
logs/scraper.log
```

Contains execution information, warnings, errors, pagination progress, and processing information.

---

## 13. Final Execution Results

The complete pipeline was executed successfully.

Final results:

| Metric | Result |
|---|---:|
| Books records | 1,000 |
| Quotes records | 100 |
| Total raw records | 1,100 |
| After cleaning | 1,100 |
| Rejected records | 0 |
| Duplicates removed | 1 |
| Final records | 1,099 |
| Execution time | 282.72 seconds |

Per-source results:

| Source | Raw | Cleaned | Rejected | Duplicates | Final |
|---|---:|---:|---:|---:|---:|
| Books to Scrape | 1,000 | 1,000 | 0 | 1 | 999 |
| Quotes to Scrape | 100 | 100 | 0 | 0 | 100 |

---

## 14. Installation

Create and activate a Python virtual environment:

### Windows PowerShell

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

---

## 15. Running the Scraper

From the project root:

```powershell
python main.py
```

The pipeline will scrape both sources and generate:

```text
output/final_dataset.csv
output/summary_report.json
logs/scraper.log
```

---

## 16. Running Tests

Run the automated test suite with:

```powershell
pytest
```

The current automated processor test suite contains six tests covering:

- Price cleaning
- Rating cleaning
- Text cleaning
- Record validation
- Invalid price handling
- Deduplication

The tests can be executed without running the complete web scraping pipeline.

---

## 17. Reproducibility

The project includes:

```text
requirements.txt
```

to document Python dependencies.

The processing and scraping logic is separated into modules so that individual components can be tested independently.

The final output metrics and execution information are recorded in the JSON summary report.

---

## 18. AI Usage

AI assistance was used during development for code suggestions, debugging, test design, documentation assistance, and implementation guidance.

All generated suggestions were reviewed and tested before being incorporated into the project.

See:

```text
AI_USAGE.md
```

for additional information about AI-assisted development and validation.

---

## 19. Limitations

The project is designed for the two specified demonstration websites.

The scrapers depend on the HTML structure of those websites. If the sites change their HTML structure, selectors may need to be updated.

The project does not use browser automation because the required data is available in server-rendered HTML.

---

## 20. Assignment Deliverables

The project provides:

- Separate source-specific scraper modules
- Common normalized data model
- Dynamic pagination
- Data cleaning
- Data validation
- Deduplication
- Error handling
- Retry handling
- Logging
- Consolidated CSV output
- JSON summary report
- Automated tests
- `requirements.txt`
- `README.md`
- `AI_USAGE.md`