# GID
GisAids Influenza Downloader

## Introduction
This project is used to download data from the EpiFlu(influenza virus database) in GISAID, including metadata, genetic sequences, etc.

## Limit
 - *search_page.py* can only be used to download all entries from EpiFlu, without the ability to filter specific datasets.
 - *download_item.py* selects up to 8,000 data entries each time. You need to manually click the 'Download' button in the browser, select the required file type, and then manually download the file.
 - Each time *download_item.py* initiates a download , the program opens a new browser page for login.

## Prerequisites
Before you begin using this script, ensure that your system meets the following requirements:
1. **GisAids Account**
2. **Operating System**: Linux desktop environment is required for proper execution of the script.
3. **Firefox Browser**: This script uses Selenium, which requires Firefox browser to be installed on your machine. Install Firefox if it is not already installed.
4. **Firefox WebDriver**: You will also need to download the Firefox WebDriver, which allows Selenium to interact with Firefox. The WebDriver can be downloaded from the following URL:
   - [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
   
   After downloading, extract the WebDriver and place it in the root directory of the project.

## Setup
1. **Clone the Repository**: First, clone this repository to your local machine using Git.
2. **Set up Conda Environment**: Use the `environment.yml` file to create a Conda environment with all the necessary dependencies:
   ```bash
   conda env create -f environment.yml
   ```

## Usage
Follow these steps to use this project:
1. In the `download_item.py` and `search_page.py` files, fill in `username = ''` and `password = ''`, as well as the `page_number` variable with the username, password, and maximum number of pages.
2. Execute the `search_page.py` program to download all search page entry information:
   ```bash
   python search_page.py
   ```
3. After the download is complete, execute combine_json.py to merge all the page information:
   ```bash
   python combine_json.py
   ```
4. Execute download_item.py to download the required entry data:
   ```bash
   python download_item.py 
   ```
