from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import logging
import sys
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import time


logging.basicConfig(
    filename='manchester.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filemode='a'
)

class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.strip() != '':
            self.level(message)

    def flush(self):
        pass  
sys.stdout = LoggerWriter(logging.info)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger().addHandler(console_handler)

def bridgewater_hall():
    section_names=['Choir','Choir Circle','Circle','Circle Alcove','Circle Center','Gallery','Gallery Center','Side Circle','Side Gallery','Stalls']
    max_seat=6
    response=requests.get('https://www.bridgewater-hall.co.uk/whats-on/').text
    soup=BeautifulSoup(response,'lxml')
    total_pages=len(soup.find_all('a',class_='page-numbers'))
    print(total_pages)
    for event in soup.find_all('div',class_='c-event-item__body o-media__body'):
        book_tickets_link = event.find("a", class_="c-btn c-btn--book")
        if book_tickets_link is None:
            continue
        book_tickets_url = book_tickets_link["href"]
        event_name=event.find("h3", class_="c-event-item__heading").get_text(strip=True)
        event_date=event.find("p", class_="c-event-item__meta-item c-event-item__datetime").get_text(strip=True)
        event_date = datetime.strptime(event_date, "%A %d %B %Y %I.%M%p")
        formatted_event_date = event_date.strftime("%Y-%m-%d %H:%M")
        event_venue = event.find("p", class_="c-event-item__meta-item c-event-item__location")
        if event_venue is None:
            continue
        event_venue=event_venue.get_text(strip=True)
        event_venue = event_venue.replace("fas fa-map-marker-alt", "").strip()
        if event_venue!='The Bridgewater Hall':
            continue
        print(f"{event_name}====={formatted_event_date}")
        perf_id=book_tickets_url.split("/")[-1]
        response=requests.get(f'https://tickets.bridgewater-hall.co.uk/api/syos/GetPerformanceDetails?performanceId={perf_id}')
        facility_no=response.json()['facility_no']
        response=requests.get(f'https://tickets.bridgewater-hall.co.uk/api/syos/GetScreens?performanceId={perf_id}')
        screen_ids=[]
        for m in response.json():
            if m['Available']==True:
                screen_ids.append(m['screen_no'])
        for screen_no in screen_ids:
            response=requests.get(f'https://tickets.bridgewater-hall.co.uk/api/syos/GetSeatList?performanceId={perf_id}&facilityId={facility_no}&screenId={screen_no}')
            for holdcode in response.json()['holdCodes']:
                if holdcode['hc_desc']=='Unassigned':
                    hold_code=holdcode['hc_no']
            prices_zones={}
            seats={}
            for zone_price in response.json()['ZoneColorList']:
                prices_zones[zone_price['zone_no']]=zone_price['price']
            for seat in response.json()['seats']:
                if seat['HoldCode']!=hold_code:
                    print('HoldCode did not match')
                    continue
                if seat['seat_status_desc']=='Unavailable':
                    continue
                try:
                    seat_price=prices_zones[seat['zone_no']]
                except:
                    continue
                seat_row=seat['seat_row']
                seat_num=seat['seat_num']
                seat_section=seat['ZoneLabel']
                if seat_section in section_names:
                    if seat_section not in seats:
                        seats[seat_section]={}
                        seats[seat_section][seat_row]=[]
                        seats[seat_section][seat_row].append(seat_num)
                    else:
                        try:
                            seats[seat_section][seat_row].append(seat_num)
                        except:
                            seats[seat_section][seat_row]=[]
                        seats[seat_section][seat_row].append(seat_num)
            print('**************************')
            print(seats)
            print('**************************')
    for page_no in range(2,total_pages+1):
        print('====================================================')
        response=requests.get(f'https://www.bridgewater-hall.co.uk/whats-on/page/{page_no}').text
        soup=BeautifulSoup(response,'lxml')
        for event in soup.find_all('div',class_='c-event-item__body o-media__body'):
            book_tickets_link = event.find("a", class_="c-btn c-btn--book")
            if book_tickets_link is None:
                continue
            book_tickets_url = book_tickets_link["href"]
            event_name=event.find("h3", class_="c-event-item__heading").get_text(strip=True)
            event_date=event.find("p", class_="c-event-item__meta-item c-event-item__datetime").get_text(strip=True)
            event_date = datetime.strptime(event_date, "%A %d %B %Y %I.%M%p")
            formatted_event_date = event_date.strftime("%Y-%m-%d %H:%M")
            event_venue = event.find("p", class_="c-event-item__meta-item c-event-item__location")
            if event_venue is None:
                continue
            event_venue=event_venue.get_text(strip=True)
            event_venue = event_venue.replace("fas fa-map-marker-alt", "").strip()
            if event_venue!='The Bridgewater Hall':
                continue
            print(f"{event_name}====={formatted_event_date}===={event_venue}===={book_tickets_url}")
            perf_id=book_tickets_url.split("/")[-1]
            response=requests.get(f'https://tickets.bridgewater-hall.co.uk/api/syos/GetPerformanceDetails?performanceId={perf_id}')
            facility_no=response.json()['facility_no']
            max_seat=response.json()['MaxSeats']
            response=requests.get(f'https://tickets.bridgewater-hall.co.uk/api/syos/GetScreens?performanceId={perf_id}')
            screen_ids=[]
            for m in response.json():
                if m['Available']=='true':
                    screen_ids.append('screen_no')
            for screen_no in screen_ids:
                response=requests.get(f'https://tickets.bridgewater-hall.co.uk/api/syos/GetSeatList?performanceId={perf_id}&facilityId={facility_no}&screenId={screen_no}')
                print(response.text)
                prices_zones={}
                seats={}
                for zone_price in response.json()['ZoneColorList']:
                    prices_zones[zone_price['zone_no']]=zone_price['price']
                for seat in response.json()['seats']:
                    if seat['seat_status_desc']=='Unavailable':
                        continue
                    try:
                        seat_price=prices_zones[seat['zone_no']]
                    except:
                        continue
                    seat_row=seat['seat_row']
                    seat_num=seat['seat_num']
                    seat_section=seat['ZoneLabel']
                    if f"{seat_section}_{seat_row}_{seat_price}" not in seats:
                        seats[f"{seat_section}_{seat_row}_{seat_price}"]=[seat_num]
                    else:
                        seats[f"{seat_section}_{seat_row}_{seat_price}"].append(seat_num)
                print('******************************')
                print(seats)
                print('**************************')
    '''
                    




bridgewater_hall()


def o2appollomanchester():
    response=requests.get('https://www.academymusicgroup.com/o2apollomanchester/events/all')
    soup = BeautifulSoup(response.text, "lxml")

    month_mapping = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }

    
    events = []
    current_month = None
    current_year = None
    for element in soup.find("div", class_="view-content").find_all(["h3", "article"], recursive=True):

        if element.name == "h3":
            month_year_text = element.text.strip()
            parts = month_year_text.split()
            if len(parts) == 2:
                current_month, current_year = parts[0], parts[1]

        elif element.name == "article" and current_month and current_year:
            date_info = element.find("div", class_="event-date")
            event_info = element.find("div", class_="event-info")
            ticket_link = element.find("a", class_="buy-btn")

            if date_info and event_info:
                day_name = date_info.find("span", class_="day").text.strip() if date_info.find("span", class_="day") else ""
                day_number = date_info.find("span", class_="date").text.strip() if date_info.find("span", class_="date") else ""
                time_24 = date_info.find("span", class_="time").text.strip() if date_info.find("span", class_="time") else ""

                try:
                    time_24h = datetime.strptime(time_24, "%I.%M%p").strftime("%H-%M")
                except ValueError:
                    time_24h = "00-00" 

                formatted_date = f"{current_year}-{month_mapping.get(current_month, '01')}-{day_number.zfill(2)} {time_24h}"

                event_name = event_info.find("h3").text.strip() if event_info.find("h3") else ""
                event_place = event_info.find("div", class_="field-item").text.strip() if event_info.find("div", class_="field-item") else ""
                if event_place!='O2 Apollo Manchester':
                    continue
                ticket_url = ticket_link["href"] if ticket_link else "No Ticket Available"
                if ticket_url =="No Ticket Available":
                    continue
                events.append({
                    "Event Date": formatted_date,
                    "Event Name": event_name,
                    "Ticket Link": ticket_url
                })
    driver=uc.Chrome()
    for event in events:
        time.sleep(3)
        link=event['Ticket Link']
        print(link)
        '''
        driver.get(link)
        selenium_cookies = driver.get_cookies()
        session=requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=cookie.get('domain'),
            path=cookie.get('path'),
            expires=cookie.get('expiry'),
            secure=cookie.get('secure', False),
            rest={'HttpOnly': cookie.get('httpOnly', False)})
        
        '''
        url = f"https://www.ticketmaster.co.uk/api/quickpicks/{link.split('/')[4].split('?')[0]}/list"

        params = {
            "sort": "price",
            "offset": "0",
           # "qty": "2",
            "primary": "true",
            "resale": "true",
            "defaultToOne": "true",
           # "tids": "000000000001"
        }

        headers = {
            "sec-ch-ua-platform": '"Linux"',
            "Referer": link,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            print(response.json())  
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")


    #response=requests.get('https://www.ticketmaster.co.uk/api/quickpicks/36006159A9B112EB/list?sort=price&offset=0&qty=2&primary=true&resale=true&defaultToOne=true&tids=000000000002%2CSODK6BV7CZE%2C000000000003')
    #response=requests.get('https://www.ticketmaster.co.uk/api/quickpicks/36006159A9B112EB/list?sort=price&offset=0&qty=2&primary=true&resale=true&defaultToOne=true')
    #print(response.text)

#o2appollomanchester()


