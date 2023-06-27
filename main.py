import aiohttp
import asyncio
import logging
import platform
import time
from datetime import datetime, timedelta


pb_url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

reference_currencies = [
                        'AUD',
                        'AZN',
                        'BYN',
                        'CAD',
                        'CHF',
                        'CNY',
                        'CZK',
                        'DKK',
                        'EUR',
                        'GBP',
                        'GEL',
                        'HUF',
                        'ILS',
                        'JPY',
                        'KZT',
                        'MDL',
                        'NOK',
                        'PLN',
                        'SEK',
                        'SGD',
                        'TMT',
                        'TRY',
                        'UAH',
                        'USD',
                        'UZS',
                        'XAU'
                        ]


class PBCollector:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def get_currency(self, foreign_currency, days: int):
        async with self.session as session:
            tasks = []
            today = datetime.today()
            for i in range(days):
                day = (today - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(self.get_currency_rate(session, foreign_currency, day))
            results = await asyncio.gather(*tasks)
            return results

    @staticmethod
    async def get_currency_rate(session: aiohttp.ClientSession, foreign_currency: str, day: str):
        logging.debug('Started!')
        start = time.time()
        async with session.get(pb_url+day) as response:
            full_result = await response.json()
            exchange_rates = full_result['exchangeRate']
            
            result = list(filter(lambda exchange_rate: exchange_rate['currency'] == foreign_currency, exchange_rates))
            
            finish = time.time()
            logging.info(f'done in {finish - start:.4f} sec.')
            return result


async def main(foreign_currency, days):
    pb = PBCollector()
    logging.info(f"Getting currency rate for the past {days} days.")
    result = await pb.get_currency(foreign_currency, days)

    logging.debug("Results:")
    for i in result:
        logging.debug(i)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(funcName)s %(message)s')
    days = int(input("Enter the number of days (no more than 5): \n>>> "))
    if days not in range(1,6):
        logging.info("Out of range lmao")
    else:
        foreign_currency = input("Enter foreign_currency (like 'EUR' or 'USD'): \n>>> ")
        if foreign_currency not in reference_currencies:
            logging.info(f"Unknown currency")
        else:
            if platform.system() == 'Windows':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(main(foreign_currency, days))