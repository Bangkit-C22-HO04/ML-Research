from asyncore import write
import requests
from bs4 import BeautifulSoup
import re
import csv

def fetch_hotels(city, search_url):
    """Fetch hotel data by a single traveloka search url"""
    hotel_data = []
    hotel_links = []
    
    page = '&skip='
    next = '-next'
    url = search_url

    # Loop range ADJUSTABLE, with +- 19 hotel data each page
    for i in range(3):
        if i != 0:
            url = search_url + page + str(i) + next
        
        search_response = requests.get(url).content
        search_soup = BeautifulSoup(search_response, 'html.parser')
        divs = search_soup.find_all('a', {'class': '_16TPR'})
        name = search_soup.find_all('h3', {'class': '_20SY_ tvat-hotelName'})
        prices = search_soup.find_all('span', {'class': '_2c6V9 tvat-hotelPrice'})
        rating_score = search_soup.find_all('span', {'class':'tvat-ratingScore'})
        total_review = search_soup.find_all('span', {'class':'_227z0'})

        # access each hotel detail 
        for a in range(len(divs)):
            link = re.search(r"^<a class=\"_16TPR\" href=\"(.*?)target", str(divs[a])).group(1)
            hotel_links.append(link[:-2])

            hotel_response = requests.get(link).content
            hotel_soup = BeautifulSoup(hotel_response, 'html.parser')
            hotel_type = hotel_soup.find('div', {'class': '_1N7FT'}).text

            id = link.split('/')[6].split('?')[0].split('-')[-1]

            hotel = {
                'id': id, 
                'hotel_name': name[a].decode_contents(),
                'hotel_city': city,
                'hotel_price': prices[a].decode_contents(),
                'hotel_type': hotel_type,
                'hotel_rating': rating_score[a].decode_contents(),
                'total_review': total_review[a].decode_contents()[1:-1]

            }
            hotel_data.append(hotel)
    return hotel_data, hotel_links

def run_fetch(urls):
    """Fetch and collect all hotel data by urls"""

    labels = ['id', 'hotel_name', 'hotel_city', 'hotel_price', 'hotel_type', 'hotel_rating', 'total_review']

    all_hotel_data, all_hotel_links = [], []

    for city in urls:
        hotel_data, hotel_links = fetch_hotels(city, urls.get(city))
        all_hotel_data.extend(hotel_data)
        all_hotel_links.extend(hotel_links)
    
    return labels, all_hotel_data, all_hotel_links

def export_csv(filename, column, data):
    """Export list of dictionary to CSV"""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column)
            writer.writeheader()
            writer.writerows(data)
    except IOError:
        print("I/O error")

    
def main():
    urls = {
        # adjustable pake domain https://m.traveloka.com
        'Yogyakarta': 'https://m.traveloka.com/en-id/hotel/search/GEO_CITY.107442.1.31-12-2022.01-01-2023?guests=1&rooms=1',
        'Bali': 'https://m.traveloka.com/en-id/hotel/search/GEO_REGION.102746.2.31-12-2022.01-01-2023?&guests=1&rooms=1',
        'Jakarta': 'https://m.traveloka.com/en-id/hotel/search/GEO_REGION.102813.1.31-12-2022.01-01-2023?guests=1&rooms=1',
        'Surabaya': 'https://m.traveloka.com/en-id/hotel/search/GEO_CITY.103570.1.31-12-2022.01-01-2023?guests=1&rooms=1', 
        'Bandung': 'https://m.traveloka.com/en-id/hotel/search/GEO_CITY.103859.1.31-12-2022.01-01-2023?guests=1&rooms=1' 
    }
    labels, hotel_data, hotel_links = run_fetch(urls)
    #print(hotel_data)

    #adjustable file name
    export_csv('hotels.csv', labels, hotel_data)
    print(hotel_links)


if __name__ == "__main__":
    main()
