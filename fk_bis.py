import requests
import json
import logging

class FlipkartScraper:
    def __init__(self, tg_api_key, tg_grp_id, min_perc):
        self.session = requests.Session()
        self.headers = {
            'Host': 'www.flipkart.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Mode': 'cors',
            'x-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36 FKUA/website/41/website/Desktop',
            'DNT': '1',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Accept': '/',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://www.flipkart.com/',
            'Origin': 'https://www.flipkart.com',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.tg_api_key = tg_api_key
        self.tg_grp_id = tg_grp_id
        self.min_perc = min_perc

    def fetch_data(self, url):
        requrl = "https://www.flipkart.com/api/4/page/fetch?cacheFirst=false"
        jsondata = {"pageUri": url, "pageContext": {"fetchSeoData": True}}

        try:
            response = self.session.post(requrl, headers=self.headers, json=jsondata)
            response.raise_for_status()
            jdata = response.json()
            logging.debug(f"Raw JSON data: {json.dumps(jdata, indent=2)}")
        except (requests.RequestException, json.JSONDecodeError) as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return None

        return jdata

    def process_data(self, jdata):
        try:
            pagedata = jdata['RESPONSE']['pageData']
            title = pagedata['pageContext']['titles']['title']
            price = int(pagedata['pageContext']['fdpEventTracking']['events']['psi']['ppd']['finalPrice'])
            lid = pagedata['pageContext']['fdpEventTracking']['events']['psi']['pls']['listingId']
            state = pagedata['pageContext']['fdpEventTracking']['events']['psi']['pls']['availabilityStatus']
            image = pagedata['pageContext']['imageUrl']
            image = image.replace('{@width}', '500').replace('{@height}', '500').replace('{@quality}', '70')
            return title, price, lid, state, image
        except KeyError as e:
            logging.error(f"Error processing data: {e}")
            return None, None, None, None, None

    def send_telegram_message(self, title, price, lid, state, image, url):
        if price <= int(self.min_perc) and state == "IN_STOCK":
            msg = f"<b>[{state}] {title}</b>\n"
            msg += f"Given Price: <b>Rs. {self.min_perc}</b>\n"
            msg += f"Price: <b>Rs. {price}</b>\n"
            msg += f"{url}\n\n"

            tg_url = f'https://api.telegram.org/bot{self.tg_api_key}/sendPhoto'
            data = {'chat_id': self.tg_grp_id, 'photo': image, 'caption': msg, 'parse_mode': 'html'}
            try:
                response = self.session.post(tg_url, data=data)
                response.raise_for_status()
            except requests.RequestException as e:
                logging.error(f"Error sending Telegram message: {e}")

    def run(self, url):
        jdata = self.fetch_data(url)
        if jdata:
            print(self.process_data(jdata))
            title, price, lid, state, image = self.process_data(jdata)
            if title and price is not None and state and image:
                self.send_telegram_message(title, price, lid, state, image, url)


while True:
    logging.basicConfig(level=logging.DEBUG)
    TG_API_KEY = '5754286532:AAGd6nTuYAZkORvVtPILRASMZYDuO4m9Ih4'
    TG_GRP_ID = '-1001625406562'
    MIN_PERC = '7699'
    url = 'https://www.flipkart.com/motorola-g62-5g-midnight-gray-128-gb/p/itm37da299ffb2d0?pid=MOBGEDT5ZZMZQZSJ&lid=LSTMOBGEDT5ZZMZQZSJJDYCEV'
    scraper = FlipkartScraper(TG_API_KEY, TG_GRP_ID, MIN_PERC)
    scraper.run(url)