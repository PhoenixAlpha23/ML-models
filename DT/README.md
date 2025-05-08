# Probiotics Web Scraper  

## Overview  
This project focuses on the task of extracting relevant data from a list of company websites to help a probiotics company analyze key attributes across three verticals:  
1. **Food & Beverages (F&B)**  
2. **Bulk (probiotic strains for product creation)**  
3. **Formulations (end products)**  

The goal was to perform keyword-based analysis and generate a structured CSV file with binary responses (`Yes/No`) for various attributes, making the data easy to analyze and draw insights from.  

---

## Features  
- **Keyword-Based Extraction**: Identifies the presence of relevant terms like `Probiotics`, `Gut Health`, `Fortification`, etc., from web page content.  
- **Structured Output**: Creates a CSV file with attributes like `Manufacturer`, `Brand`, `Distributor`, and specific health-related keywords for each company.  
- **Scalable**: Easily configurable to scrape multiple websites.  
- **Customizable**: Add or modify keywords and attributes as needed.  

---

## Installation  

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/PhoenixAlpha23/ML-models/new/main/DT
   ```
   Or you can open the notebook in Google Colab directly.
   
3. **Install Dependencies**  
   Use `pip` to install the required libraries:  
   ```bash
   pip install requests beautifulsoup4 pandas
   ```  

4. **Add Websites**  
   Update the `company_urls` list in the script with the URLs of websites to scrape.  

---

## Usage  

1. Run the script:  
   ```bash
   python scraper.py
   ```  
2. The script will scrape each website for the specified keywords and generate a file named `keyword_analysis.csv`.  

---

## Output Format  

The output CSV file includes the following attributes for each website:  
- **URL**  
- **Relevant Category**  
- **Manufacturer**  
- **Brand**  
- **Distributor**  
- **F&B**  
- **Probiotics**  
- **Fortification**  
- **Gut Health**  
- **Womens Health**  
- **Cognitive Health**  

Each column will have `Yes` or `No` based on the presence of keywords.  

---

## Customization  

1. **Modify Keywords**  
   Update the `keywords` dictionary in the script to include additional terms or attributes.  

2. **Extend Attributes**  
   Add new keys and corresponding keywords to expand the data extraction scope.  

---

## Future Enhancements  
- Integrate advanced text analysis for better keyword matching.  
- Implement scraping for dynamic content using `Selenium`.  
- Automate periodic data scraping and updates.  

---

## License  
This project , as for all others in this repository ,is licensed under the MIT License. 
