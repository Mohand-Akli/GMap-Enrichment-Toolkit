# Restaurant Scraping & Data Processing Pipeline

This Python script utilizes a modular framework to perform web scraping, data enrichment, cleaning, and interactive manual validation for restaurant datasets. It features an interactive color-coded terminal menu and seamless Google Maps visual verification.

## Read Prerequisites
Latest python was not used and is not suggested

<br>
To do a custom web scraping project you can find me on GitHub or LinkedIn<br><br>

<a href="https://github.com/Mohand-Akli" target="_blank">
<img src=https://img.shields.io/badge/GitHub-181717?&style=for-the-badge&logo=github&logoColor=white alt=github style="margin-bottom: 5px;" />
</a>

<a href="https://www.linkedin.com" target="_blank">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?&style=for-the-badge&logo=linkedin&logoColor=white" alt="linkedin" style="margin-bottom: 5px;" />
</a>


## Table of Contents
- [Prerequisites](#prerequisites)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Notes](#notes)
- [License](#license)

## Prerequisites
- Python 3.8 or higher installed on your system.
- Google Chrome or a compatible browser installed (for map visualization and automation).

## Key Features
- **Interactive Menu (`scrapper.py`)**: A centralized, color-coded terminal dashboard to launch all functional modules easily.
- **Global Pipeline (`main.py`)**: Automates initial geographic data extraction and dataset merging.
- **Interactive Cleaning & Validation (`data_processor.py`)**: Features a row-by-row manual verification process that automatically opens Google Maps for each restaurant so you can check photos and reviews before deciding to keep or discard entries.
- **Email Scraping (`email_scraper.py`)**: Extracts contact email addresses automatically.
- **Google Maps Scraping (`gmaps_scrapper.py`)**: Fetches detailed metadata including ratings, review counts, place types, and operating hours.
- **Phone Number Recovery (`phone_scraper.py`)**: Collects and formats restaurant telephone numbers.
- **VAT Finder (`vat_finder.py`)**: Identifies corporate and business VAT numbers.

## Installation

1. Clone this repository:
   ```bash
   git clone [https://github.com/Mohand-Akli/scrapper.git](https://github.com/Mohand-Akli/scrapper.git)
   cd scrapper
