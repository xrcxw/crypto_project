import numpy as np
from decimal import Decimal


def calculate_volatility(prices_list):
    """Рассчитывает годовую волатильность на основе дневных цен"""
    if len(prices_list) < 2:
        return Decimal('0')

    log_returns = []
    for i in range(1, len(prices_list)):
        if prices_list[i - 1] > 0:
            ret = np.log(float(prices_list[i] / prices_list[i - 1]))
            log_returns.append(ret)

    if not log_returns:
        return Decimal('0')

    volatility = np.std(log_returns) * np.sqrt(365)
    return Decimal(str(round(volatility * 100, 2)))


def calculate_return_percent(start_price, end_price):
    """Процент изменения цены за период"""
    if start_price == 0:
        return Decimal('0')
    return ((end_price - start_price) / start_price) * 100


def get_recommendation(volatility_percent):
    """Текстовый совет на основе волатильности"""
    if volatility_percent > 80:
        return "⚠️ Высокая волатильность — повышенный риск"
    elif volatility_percent > 40:
        return "📊 Средняя волатильность — умеренный риск"
    else:
        return "✅ Низкая волатильность — более стабильный актив"