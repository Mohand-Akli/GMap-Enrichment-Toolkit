# Google Maps Scraper

This Python toolset utilizes Playwright and specialized scraping modules to perform comprehensive data extraction. Based on your project structure, it goes beyond basic Google Maps scraping by incorporating dedicated modules to find emails, phone numbers, and VAT information for businesses.

<br>

<a href="https://www.linkedin.com/in/mohand-akli-zidani" target="_blank">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?&style=for-the-badge&logo=linkedin&logoColor=white" alt="linkedin" style="margin-bottom: 5px;" />
</a>

## Table of Contents
- [Prerequisites](#prerequisites)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Notes](#notes)
- [License](#license)

## Prerequisites
- Python 3.8 or 3.9 (Python 3.10+ may not be compatible with some dependencies)
- Google Chrome or Chromium browser installed (for Playwright)

## Key Features
- **Google Maps Scraping:** Extract business names, addresses, websites, ratings, and operating hours (`gmaps_scrapper.py`).
- **Email Extraction:** Crawl associated business websites to locate and extract contact email addresses (`email_scraper.py`).
- **Phone Number Scraping:** Parse websites and listings to identify direct contact numbers (`phone_scraper.py`).
- **VAT Finder:** Automatically detect and extract Value Added Tax (VAT) numbers for corporate entities (`vat_finder.py`).
- **Data Cleansing & Processing:** Organize and format the raw extracted data into clean, export-ready structures (`data_processor.py`).
- **CSV Export:** Save all aggregated business intelligence into a consolidated CSV file.

## Project Structure
```text
├── requirements.txt
├── scrapper.py
└── src/
    ├── __init__.py
    ├── data_processor.py
    ├── email_scraper.py
    ├── gmaps_scrapper.py
    ├── main.py
    ├── phone_scraper.py
    └── vat_finder.py
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

Run the main script to initiate the extraction pipeline:

```bash
python src/main.py -s "IT Companies in Paris, France" -t 20 -o results.csv
```

- `-s` or `--search`: Search query for target businesses.
- `-t` or `--total`: Number of results to scrape.
- `-o` or `--output`: Output CSV file path.
- `--append`: Append results to the output file instead of overwriting.

## Notes
- The script relies on Playwright and may open a visible browser window depending on your configuration.
- DOM structures on Google Maps and third-party websites change frequently; you may need to update selectors in the respective `src/` modules if extractions fail.
- Avoid running too many concurrent scrapes in a short period to prevent rate-limiting or blocks.

## License
MIT
