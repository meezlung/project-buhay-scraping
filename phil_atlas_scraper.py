"""
Simple webscraper for barangay information from PhilAtlas and Wikipedia
"""

import json
import csv
from typing import TypeAlias
from bs4 import BeautifulSoup, Tag, NavigableString
import requests
from requests import Response

FieldName: TypeAlias = str

class PhilAtlas:
    """ 
    Module for scraping barangay information from PhilAtlas 
    """

    def __init__(self, barangay_districts: dict[int, list[str]]) -> None:
        """ Initialize the main URL and data containers """
        self.url = 'https://www.philatlas.com/luzon/ncr/quezon-city.html'
        self.barangays: list[dict[FieldName, str | int | float]] = []
        self.barangay_districts = barangay_districts

    def main(self) -> None:
        """ Main function to run the scraper """
        response = self.get_url_response(self.url)
        soup = self.parse_html_from_response(response)
        table = self.get_table(soup)

        if isinstance(table, Tag): # Check if table is found
            tbody = self.get_barangay_table_body(table)
            self.get_barangay_information(tbody)

        else:
            print("Table not found or is not a valid tag.")

    def get_url_response(self, url: str) -> Response:
        """ Fetches response from a given URL """
        response = requests.get(url, timeout=30) # Wait for a maximum of 30 seconds for the response
        response.raise_for_status()
        return response

    def parse_html_from_response(self, response: Response) -> BeautifulSoup:
        """ Parses HTML content from a response """
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def get_table(self, soup: BeautifulSoup) -> Tag | NavigableString | None:
        """ Finds and returns the main table containing all barangays with their information """
        table = soup.find('table', {'class': 'sortable datatable', 'id': 'lguTable'})
        return table

    def get_barangay_table_body(self, table: Tag) -> Tag | NavigableString | None:
        """ Returns the table body of the main table """
        tbody = table.find('tbody')
        return tbody if tbody else None

    def get_barangay_information(self, tbody: Tag | NavigableString | None) -> None:
        """ Extracts information from each barangay """
        if isinstance(tbody, Tag):
            for row in tbody.find_all('tr'):

                # Extract each field from the row
                barangay_name: str = self.get_barangay_name(row)
                district_number: int = self.get_district_number(barangay_name)
                population_data_2015, population_data_2020 = self.get_population_data(row)
                household_population_2015: int = -1
                household_count_2015: int = -1
                average_household_size_2015: float = -1

                # Access the demographics table with graphs
                barangay_demographics = self.open_barangay_link(row)

                # Find demographics data table (the one with graphs)
                if isinstance(barangay_demographics, Tag):
                    household_population_2015, household_count_2015, average_household_size_2015 = self.get_demographics_data(barangay_demographics)
                    self.append_all_data(barangay_name, district_number, population_data_2015, population_data_2020, household_population_2015, household_count_2015, average_household_size_2015)
                    print(f"Successfully extracted data for {barangay_name}.")

                else:
                    print("Demographics table not found or is not a valid tag.")
                    self.append_all_data(barangay_name, district_number, population_data_2015, population_data_2020, household_population_2015, household_count_2015, average_household_size_2015)

        else:
            print("tbody not found or is not a valid tag.")

    def get_barangay_link(self, row: Tag) -> str:
        """ Retrieves the barangay-specific link for each row """
        barangay_tag = row.find('th')

        if barangay_tag:
            link_tag = barangay_tag.find('a')

            if isinstance(link_tag, Tag):
                barangay_link = str(link_tag['href'])
                website_link = 'https://www.philatlas.com/'
                barangay_link = website_link + barangay_link # This is because the link is relative
                return barangay_link

        return ""

    def open_barangay_link(self, row: Tag) -> Tag | NavigableString | None:
        """ Opens the barangay-specific link and parses the page for demographics data """
        barangay_link = self.get_barangay_link(row)
        barangay_response = self.get_url_response(barangay_link)
        barangay_soup = self.parse_html_from_response(barangay_response)
        barangay_demographics = self.find_barangay_demographics(barangay_soup)
        return barangay_demographics

    def find_barangay_demographics(self, barangay_soup: BeautifulSoup) -> Tag | NavigableString | None:
        """ Looks for the demographics table with graphs in the barangay-specific page """
        barangay_demographics = barangay_soup.find('table', {'class': 'chart-table', 'id': 'households-table'})
        return barangay_demographics

    def get_barangay_name(self, row: Tag) -> str:
        """ Extracts the barangay name from the row """
        barangay_tag = row.find('th')
        if barangay_tag:
            barangay = barangay_tag.get_text(strip=True)
            return barangay
        return ""

    def get_district_number(self, barangay_name: str) -> int:
        """ Determines the district number of the barangay """

        # This are special cases where the barangay name from PhilAtlas is different from the one in Wikipedia
        special_cases = {
            'Santo Cristo': 1,
            'Santo Domingo': 1,
            'Sienna': 1,
            'N. S. Amoranto': 1,
            'Balong Bato': 2,
            'Saint Ignatius': 3,
            'Claro': 3,
            'Teachers Village East': 4,
            'Teachers Village West': 4,
            'Aurora': 4,
            'San Isidro': 4,
            'Santa Lucia': 5,
            'Santa Cruz': 5,
            'Santa Monica': 5
        }

        if barangay_name in special_cases:
            return special_cases[barangay_name]

        # Normal cases
        for district_number, barangays in self.barangay_districts.items():
            if barangay_name in barangays:
                return district_number

        return -1 # If barangay name is not found in the dictionary

    def get_population_data(self, row: Tag) -> tuple[int, int]:
        """ Extracts the population data (2015 and 2020) from the row """
        cells = row.find_all('td')
        population_data_2020_str = cells[1].get_text(strip=True)
        population_data_2015_str = cells[2].get_text(strip=True)

        population_data_2015 = self.convert_str_to_int(population_data_2015_str)
        population_data_2020 = self.convert_str_to_int(population_data_2020_str)
        return population_data_2015, population_data_2020

    def get_demographics_data(self, barangay_demographics: Tag) -> tuple[int, int, float]:
        """ Extracts household demographics data from the table (2015 data) """
        demographics_rows = barangay_demographics.find_all('tr')
        last_row = demographics_rows[-1] # Last row always contains the 2015 data
        cells = last_row.find_all('td')

        household_population_2015_str = cells[0].get_text(strip=True)
        household_count_2015_str = cells[1].get_text(strip=True)
        average_household_size_2015_str = cells[2].get_text(strip=True)

        household_population_2015 = self.convert_str_to_int(household_population_2015_str)
        household_count_2015 = self.convert_str_to_int(household_count_2015_str)
        average_household_size_2015 = float(average_household_size_2015_str)
        return household_population_2015, household_count_2015, average_household_size_2015

    def convert_str_to_int(self, string_number: str) -> int:
        """ Converts a string number to an integer"""
        return int(string_number.replace(',', ''))

    def append_all_data(self, barangay_name: str, district_number: int,
                              population_data_2015: int, population_data_2020: int,
                              household_population_2015: int, household_count_2015: int,
                              average_household_size_2015: float) -> None:
        """ Appends all collected data to the barangays list """
        self.barangays.append({
            'barangay_name': barangay_name,
            'district_number': district_number,
            'population_data_2015': population_data_2015,
            'population_data_2020': population_data_2020,
            'household_population_2015': household_population_2015,
            'household_count_2015': household_count_2015,
            'average_household_size_2015': average_household_size_2015
        })

    def print_json(self) -> None:
        """ Prints the collected data in JSON format for debugging purposes """
        print(json.dumps(self.barangays, indent=4))

    def write_to_json(self) -> None:
        """  Writes the collected data to a JSON file """
        with open('barangays.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(self.barangays, jsonfile, indent=3)

    def write_to_csv(self) -> None:
        """ Writes the collected data to a CSV file """
        with open('barangays.csv', 'w', newline='') as csvfile:
            fieldnames = self.barangays[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for barangay in self.barangays:
                writer.writerow(barangay)


class WikipediaBarangay(PhilAtlas):
    """
    Module for scraping barangay districts with their district number from Wikipedia
    This is because there are no district numbers in PhilAtlas
    """

    def __init__(self) -> None:
        """ Initialize Wikipedia URL for the district numbers of data dictionary """
        self.url = 'https://en.wikipedia.org/wiki/List_of_barangays_in_Quezon_City'
        self.districts: dict[int, list[str]] = {}

    def main(self) -> None:
        """ Main method to fetch and parse barangay districts from Wikipedia """
        response = self.get_url_response(self.url)
        soup = self.parse_html_from_response(response)
        self.extract_districts(soup)

    def extract_districts(self, soup: BeautifulSoup) -> None:
        """ Extracts barangay districts from Wikipedia and organizes them per district number via dict """
        district_tables = soup.find_all('table', {'class': 'wikitable'})
        district_number = 1

        for table in district_tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                if cols:
                    if district_number in self.districts:
                        self.districts[district_number].append(cols[0].text.strip())
                    else:
                        self.districts[district_number] = [cols[0].text.strip()]

            district_number += 1

    def display_districts(self) -> None:
        """  Prints the barangay districts per district number for debugging purposes """
        print(json.dumps(self.districts, indent=4))


if __name__ == '__main__':
    wikipedia = WikipediaBarangay()
    wikipedia.main()

    phil_atlas = PhilAtlas(wikipedia.districts)
    phil_atlas.main()
    phil_atlas.print_json()
    phil_atlas.write_to_json()
    phil_atlas.write_to_csv()
