# AI Usage

## Overview

AI tools were used as a development assistant during this assignment.

The candidate remained responsible for reviewing, modifying, testing, and validating all generated code.

## Areas Where AI Assistance Was Used

AI assistance was used for:

- Project structure suggestions
- Python web scraping implementation guidance
- BeautifulSoup selector suggestions
- Pagination handling
- Common data-model design
- Data cleaning and validation logic
- Deduplication strategy
- Logging and error handling
- Retry handling
- Pytest test-case design
- README and documentation assistance
- Debugging Python and pytest errors

## Example Prompts Used

Examples of prompts used during development included:

- "Help me create a Python web scraper for Books to Scrape."
- "How should I handle pagination dynamically with BeautifulSoup?"
- "Help me design a common schema for multiple scraped sources."
- "How can I clean currency values and ratings?"
- "How should I validate scraped records?"
- "Help me implement deduplication for records from multiple sources."
- "How can I add retry handling for connection failures and timeouts?"
- "Help me write pytest tests for the data processor."
- "Help me troubleshoot a pytest import error."

## Code Review and Modifications

AI-generated suggestions were not accepted blindly.

The generated code was reviewed and modified during implementation to match the assignment requirements and the actual HTML structure of the target websites.

Examples of modifications and decisions include:

- Verified the HTML selectors against the actual source pages.
- Tested pagination using multiple pages before running the complete scrape.
- Added handling for missing HTML elements.
- Added logging for request failures and invalid records.
- Added retry handling for failed HTTP requests.
- Implemented cleaning and validation as a separate processing layer.
- Implemented deduplication using normalized source, title/name, and author values.
- Preserved missing values as `None` or empty collections rather than inventing data.
- Investigated scraped description content against the source HTML rather than assuming the scraper caused the content.

## Testing Performed

The project was tested during development using:

- Manual scraper tests
- Multi-page scraping tests
- Full scraping execution
- Processor tests using pytest
- Final CSV inspection
- Final JSON summary inspection

The automated processor test suite currently passes all 6 tests.

## Final Validation

The complete scraping pipeline was executed successfully.

The final execution produced:

- 1,100 raw records
- 1,100 records after cleaning
- 0 rejected records
- 1 duplicate removed
- 1,099 final records

The final outputs were:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## Candidate Responsibility

AI assistance was used only as a development aid.

The candidate reviewed the implementation, executed the code, investigated errors, validated the scraped output, and made implementation decisions based on the assignment requirements and observed website behavior.