import requests
import time
from datetime import datetime
from decimal import Decimal

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def get_top_coins(limit=10):
    """Получить топ N монет"""
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '7d'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_historical_prices(coin_id, days=7):
    """Получить исторические цены"""
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }
    time.sleep(0.5)
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return [
        {
            'timestamp': datetime.fromtimestamp(ts / 1000),
            'price': Decimal(str(price))
        }
        for ts, price in data['prices']
    ]