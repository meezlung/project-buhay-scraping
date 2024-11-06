# Buhay Scraper
This repository contains web scraper developed as part of Project Buhay. The scraper extracts and organizes data essential to Project Buhay's broader goals.

## PhilAtlas Data
The **phil_atlas_scraper.py** is responsible for scraping barangay data from the PhilAtlas website and barangay districts from Wikipedia.

### Overview
The **phil_atlas_scraper.py** extracts the following information for each barangay in Quezon City:
 - Barangay name
 - District Number (from Wikipedia)
 - Population Data for 2015 and 2020
 - Household Demographics for 2015, including:
   - Household Population
   - Household Count
   - Average Household Size

### How the Scraper Works
1. Scraping Barangay Districts from Wikipedia:
   - The WikipediaBarangay class scrapes the Wikipedia page for the list of barangays in Quezon City and organizes them into a dictionary by district number. The district numbers are essential because the PhilAtlas website does not provide them.
   - You can find the Wikipedia page used [here](https://en.wikipedia.org/wiki/List_of_barangays_in_Quezon_City).   
2. Scraping Barangay Data from PhilAtlas:
   - The PhilAtlas class scrapes the [PhilAtlas website](https://en.wikipedia.org/wiki/List_of_barangays_in_Quezon_City) for data on each barangay.
3. Data Processing:
   - The scraper processes and structures the data into a list of dictionaries. Each dictionary contains the following fields:
      - barangay_name
      - district_number
      - population_data_2015
      - population_data_2020
      - household_population_2015
      - household_count_2015
      - average_household_size_2015
4. Saving the Data:
   - Once the data is collected, it is saved in both JSON and CSV formats.

### Data Outputs:
 - JSON: The data is saved in barangays.json in human-readable JSON format.
 - CSV: The data is also saved in barangays.csv.




## Rainfall Accumulation Data
Still under development...
