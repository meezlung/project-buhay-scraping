from bs4 import BeautifulSoup, Tag
import requests

url = 'https://www.philatlas.com/luzon/ncr/quezon-city.html'

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'class': 'sortable datatable', 'id': 'lguTable'})

barangay_links: list[dict[str, str | None]] = []

if isinstance(table, Tag): # Check if table is found
    tbody = table.find('tbody')

    if isinstance(tbody, Tag): # Check if tbody is found
        for row in tbody.find_all('tr'):
            
            barangay = row.find('th').get_text(strip=True)
            barangay_link = row.find('th').find('a')['href']
            website_link = 'https://www.philatlas.com/'
            barangay_link = website_link + barangay_link # This is because the link is relative

            census_date = None
            household_population_2015 = None
            number_of_households_2015 = None
            average_household_size_2015 = None

            # Open the link to get additional data
            barangay_response = requests.get(barangay_link)
            barangay_response.raise_for_status()

            barangay_soup = BeautifulSoup(barangay_response.text, 'html.parser')
            barangay_demographics = barangay_soup.find('table', {'class': 'chart-table', 'id': 'households-table'})

            if isinstance(barangay_demographics, Tag):
                barangay_demographics_rows = barangay_demographics.find_all('tr')
                
                # Last row is the the most recent data
                last_row = barangay_demographics_rows[-1]
                cells = last_row.find_all('td')
                
                census_date = last_row.find('th').get_text(strip=True)

                household_population_2015 = cells[0].get_text(strip=True)
                number_of_households_2015 = cells[1].get_text(strip=True)
                average_household_size_2015 = cells[2].get_text(strip=True)

            else: 
                print("Demographics table not found or is not a valid tag.")

            cells = row.find_all('td')
            population_percentage = cells[0].get_text(strip=True)
            population_2020 = cells[1].get_text(strip=True)
            population_2015 = cells[2].get_text(strip=True)

            barangay_links.append({
                'barangay': barangay,
                'barangay_link': barangay_link,
                'population_percentage': population_percentage,
                'population_2015': population_2015,
                'population_2020': population_2020,
                'census_date': census_date,
                'household_population_2015': household_population_2015,
                'number_of_households_2015': number_of_households_2015,
                'average_household_size_2015': average_household_size_2015
            })

    else:
        print("tbody not found or is not a valid tag.")
else:
    print("Table not found or is not a valid tag.")

# Print the barangay links as JSON
import json
print(json.dumps(barangay_links, indent=4))

# Write the barangay links to a CSV file
import csv
with open('barangay_links.csv', 'w', newline='') as csvfile:
    fieldnames = barangay_links[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for barangay_link in barangay_links:
        writer.writerow(barangay_link)