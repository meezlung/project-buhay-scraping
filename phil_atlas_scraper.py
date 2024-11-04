from typing import TypeAlias
from bs4 import BeautifulSoup, Tag, NavigableString
import requests
from requests import Response

FIELD_NAME: TypeAlias = str

class PhilAtlas:
    def __init__(self) -> None:
        self.url = 'https://www.philatlas.com/luzon/ncr/quezon-city.html'
        self.barangays: list[dict[FIELD_NAME, str | int | float]] = []

    def main(self) -> None:
        response = self.get_url_response(self.url)
        soup = self.parse_html_from_response(response)
        table = self.get_table(soup)

        if isinstance(table, Tag): # Check if table is found
            tbody = self.get_barangay_table_body(table)
            self.get_barangay_information(tbody)

        else:
            print("Table not found or is not a valid tag.")

    def get_url_response(self, url: str) -> Response:
        response = requests.get(url)
        response.raise_for_status()
        return response

    def parse_html_from_response(self, response: Response) -> BeautifulSoup:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def get_table(self, soup: BeautifulSoup) -> Tag | NavigableString | None:
        table = soup.find('table', {'class': 'sortable datatable', 'id': 'lguTable'})
        return table
    
    def get_barangay_table_body(self, table: Tag) -> Tag | NavigableString | None:
        tbody = table.find('tbody')
        return tbody

    def get_barangay_information(self, tbody: Tag | NavigableString | None) -> None:
        if isinstance(tbody, Tag):
            for row in tbody.find_all('tr'):

                # Fields
                barangay_name: str = self.get_barangay_name(row) 
                district_number: int = -1
                population_data_2015, population_data_2020 = self.get_population_data(row)
                household_population_2015: int = -1
                household_count_2015: int = -1
                average_household_size_2015: float = -1

                # Access the demographics table with graphs
                barangay_demographics = self.open_barangay_link(row)

                # Find demographics data table (the one with graphs) for household_population_2015, household_count_2015, and average_household_size_2015
                if isinstance(barangay_demographics, Tag):
                    household_population_2015, household_count_2015, average_household_size_2015 = self.get_demographics_data(barangay_demographics)
                    
                    self.append_all_data(barangay_name, district_number, population_data_2015, population_data_2020, household_population_2015, household_count_2015, average_household_size_2015)

                else:
                    print("Demographics table not found or is not a valid tag.")

        else:
            print("tbody not found or is not a valid tag.")
            return None
        
    def get_barangay_link(self, row: Tag) -> str:
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
        barangay_link = self.get_barangay_link(row)
        barangay_response = self.get_url_response(barangay_link)
        barangay_soup = self.parse_html_from_response(barangay_response)
        barangay_demographics = self.find_barangay_demographics(barangay_soup)
        return barangay_demographics

    def find_barangay_demographics(self, barangay_soup: BeautifulSoup) -> Tag | NavigableString | None:
        barangay_demographics = barangay_soup.find('table', {'class': 'chart-table', 'id': 'households-table'})
        return barangay_demographics 
    
    def get_barangay_name(self, row: Tag) -> str:
        barangay_tag = row.find('th')
        if barangay_tag:
            barangay = barangay_tag.get_text(strip=True)
            return barangay
        return ""

    def get_population_data(self, row: Tag) -> tuple[int, int]:
        cells = row.find_all('td')
        population_data_2020_str = cells[1].get_text(strip=True)
        population_data_2015_str = cells[2].get_text(strip=True)

        population_data_2015 = self.convert_str_to_int(population_data_2015_str)
        population_data_2020 = self.convert_str_to_int(population_data_2020_str)
        return population_data_2015, population_data_2020
    
    def get_demographics_data(self, barangay_demographics: Tag) -> tuple[int, int, float]:
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
        return int(string_number.replace(',', ''))

    def append_all_data(self, barangay_name: str, district_number: int, population_data_2015: int, population_data_2020: int, household_population_2015: int, household_count_2015: int, average_household_size_2015: float) -> None:
        self.barangays.append({
            'barangay_name': barangay_name,
            'district_number': -1,
            'population_data_2015': population_data_2015,
            'population_data_2020': population_data_2020,
            'household_population_2015': household_population_2015,
            'household_count_2015': household_count_2015,
            'average_household_size_2015': average_household_size_2015
        })

    def print_json(self) -> None:
        import json
        print(json.dumps(self.barangays, indent=4))

    def write_to_csv(self) -> None:
        import csv
        with open('barangays.csv', 'w', newline='') as csvfile:
            fieldnames = self.barangays[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for barangay in self.barangays:
                writer.writerow(barangay)

if __name__ == '__main__':
    phil_atlas = PhilAtlas()
    phil_atlas.main()
    phil_atlas.print_json()
    # phil_atlas.write_to_csv()