import pandas as pd
import sys
import requests
import base64
from bs4 import BeautifulSoup


def fast_people_search(file_path, proxy_scrape_api_key):
    try:
        # Load the Excel file
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        processing_sheet = 'FastPeopleSearch'
        fast_people_search_column = 'FastSearchUrl'

        # Check if sheet exists
        if processing_sheet in excel_file.sheet_names:
            # Load the sheet into a DataFrame w/ 2 header rows
            df = pd.read_excel(file_path, sheet_name=processing_sheet, engine='openpyxl')

            df['FPS Age'] = df['FPS Age'].astype(str)
            df['Full Name'] = df['Full Name'].astype(str)
            df['Current Address'] = df['Current Address'].astype(str)
            for n in range(1, 9):
                df[f'Past Address {n}'] = df[f'Past Address {n}'].astype(str)

            # Iterate over every non-header row
            for index, row in df.iterrows():
                print(f"Row {index}: {row[fast_people_search_column]}")

                # Make a request to fast people search
                html = make_request(row[fast_people_search_column], proxy_scrape_api_key)
                if html is not False:

                    # Parse data from HTML
                    data = parse_html(html)

                    # Update the DataFrame
                    df.at[index, 'FPS Age'] = data['age']
                    df.at[index, 'Full Name'] = data['full_name']
                    df.at[index, 'Current Address'] = data['current_address']
                    for i, address in enumerate(data['past_addresses']):
                        df.at[index, f'Past Address {i + 1}'] = address

                    # Save the updated DataFrame back to the Excel file in case of crash
                    with pd.ExcelWriter(file_path, mode="a", if_sheet_exists='replace', engine="openpyxl") as writer:
                        df.to_excel(writer, sheet_name=processing_sheet)

        else:
            print(f"Sheet '{processing_sheet}' not found in the Excel file.")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_html(html):
    data = {
        'age': '',
        'full_name': '',
        'current_address': '',
        'past_addresses': []
    }
    try:
        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')

        # Extract Age
        age_tag = soup.find(lambda tag: tag.name == "h3" and tag.text.strip() == "Age:")
        if age_tag:
            data['age'] = age_tag.next_sibling.strip()

        # Extract Full Name
        full_name_tag = soup.find(lambda tag: tag.name == "h3" and tag.text.strip() == "Full Name:")
        if full_name_tag:
            data['full_name'] = full_name_tag.next_sibling.strip()

        # Extract Current Address
        current_address_tag = soup.find(lambda tag: tag.name == "h3" and "Current Home Address:" in tag.text)
        if current_address_tag:
            data['current_address'] = current_address_tag.find_next('div').get_text(separator=', ', strip=True)

        # Extract "Past Addresses:"
        past_addresses_tag = soup.find(lambda tag: tag.name == "h3" and "Past Addresses:" in tag.text)
        if past_addresses_tag:
            address_divs = past_addresses_tag.find_next_sibling('div').find_all('div', class_='col-sm-12 col-md-6')
            data['past_addresses'] = [div.get_text(separator=', ', strip=True) for div in address_divs]
    except Exception as e:
        print(f"An error occurred: {e}")

    return data


def make_request(url, api_key):
    data = {
        "url": url,
        "httpResponseBody": True
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': api_key
    }
    try:
        response = requests.post(
            'https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request',
            headers=headers,
            json=data)

        if response.status_code == 200:
            json_response = response.json()
            if 'browserHtml' in json_response['data']:
                return json_response['data']['browserHtml']
            else:
                return base64.b64decode(json_response['data']['httpResponseBody']).decode()
        else:
            print("Proxy API Error:", response.status_code)
    except Exception as e:
        print(f"An error occurred for {url}")
        print(e)
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fast_people_search.py <path_to_excel_file> <proxyscrape api key>")
    else:
        arg_file_path = sys.argv[1]
        arg_api_key = sys.argv[2]
        fast_people_search(arg_file_path, arg_api_key)
