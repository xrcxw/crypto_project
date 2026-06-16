from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import time

from .models import Cryptocurrency, PriceHistory, VolatilityReport, Watchlist
from .services.coingecko_api import get_top_coins, get_historical_prices
from .utils.analytics import calculate_volatility, calculate_return_percent, get_recommendation


def index(request):
    """Главная страница"""
    coins = Cryptocurrency.objects.all().order_by('-market_cap')
    for coin in coins:
        coin.latest_report = coin.reports.order_by('-calculated_at').first()
    return render(request, 'coins/index.html', {'coins': coins})


def update_data(request):
    """Обновление данных из API"""
    try:
        coins_data = get_top_coins(limit=10)

        for coin_data in coins_data:
            coin, created = Cryptocurrency.objects.update_or_create(
                coin_id=coin_data['id'],
                defaults={
                    'name': coin_data['name'],
                    'symbol': coin_data['symbol'].upper(),
                    'current_price_usd': coin_data['current_price'],
                    'market_cap': coin_data['market_cap'],
                }
            )

            try:
                history = get_historical_prices(coin.coin_id, days=7)
                for entry in history:
                    PriceHistory.objects.get_or_create(
                        coin=coin,
                        timestamp=entry['timestamp'],
                        defaults={'price_usd': entry['price']}
                    )
                time.sleep(0.3)
            except Exception as e:
                print(f"Ошибка истории для {coin.name}: {e}")

            prices_qs = PriceHistory.objects.filter(coin=coin).order_by('timestamp')
            prices = [float(p.price_usd) for p in prices_qs]

            if len(prices) >= 2:
                volatility = calculate_volatility(prices)
                price_change = Decimal(str(coin_data.get('price_change_percentage_7d_in_currency', 0)))
                if price_change == 0 and len(prices) >= 2:
                    price_change = calculate_return_percent(prices[0], prices[-1])
                rec = get_recommendation(float(volatility))

                VolatilityReport.objects.create(
                    coin=coin,
                    period_days=7,
                    volatility_percent=volatility,
                    price_change_percent=price_change,
                    recommendation=rec
                )

        messages.success(request, "✅ Данные успешно обновлены!")
    except Exception as e:
        messages.error(request, f"❌ Ошибка: {str(e)}. Подождите 1 минуту и попробуйте снова.")

    return redirect('index')


def coin_detail(request, coin_id):
    """Детальная страница монеты"""
    coin = get_object_or_404(Cryptocurrency, id=coin_id)
    prices = PriceHistory.objects.filter(coin=coin).order_by('timestamp')
    reports = VolatilityReport.objects.filter(coin=coin).order_by('-calculated_at')

    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, coin=coin).exists()

    chart_html = None
    if prices.exists():
        dates = [p.timestamp.strftime('%Y-%m-%d') for p in prices]
        values = [float(p.price_usd) for p in prices]

        import plotly.express as px
        import plotly.offline as offline

        fig = px.line(
            x=dates,
            y=values,
            title=f'{coin.name} ({coin.symbol}) — динамика цены',
            labels={'x': 'Дата', 'y': 'Цена, USD'}
        )
        fig.update_layout(template='plotly_dark')
        chart_html = offline.plot(fig, output_type='div', include_plotlyjs='cdn')

    context = {
        'coin': coin,
        'chart_html': chart_html,
        'latest_report': reports.first(),
        'reports': reports[:10],
        'is_in_watchlist': is_in_watchlist,
    }
    return render(request, 'coins/detail.html', context)


def add_to_watchlist(request, coin_id):
    """Добавление в избранное"""
    if not request.user.is_authenticated:
        messages.warning(request, "Войдите в админку, чтобы добавить в избранное")
        return redirect('coin_detail', coin_id=coin_id)

    coin = get_object_or_404(Cryptocurrency, id=coin_id)
    Watchlist.objects.get_or_create(user=request.user, coin=coin)
    messages.success(request, f"⭐ {coin.name} добавлен в список отслеживания")
    return redirect('coin_detail', coin_id=coin_id)


def remove_from_watchlist(request, coin_id):
    """Удаление из избранного"""
    if not request.user.is_authenticated:
        messages.warning(request, "Войдите в систему")
        return redirect('index')

    coin = get_object_or_404(Cryptocurrency, id=coin_id)
    Watchlist.objects.filter(user=request.user, coin=coin).delete()
    messages.success(request, f"🗑️ {coin.name} удалён из избранного")
    return redirect('watchlist')


def watchlist(request):
    """Страница избранного"""
    if not request.user.is_authenticated:
        messages.warning(request, "Войдите в систему для просмотра избранного")
        return redirect('index')

    watch_items = Watchlist.objects.filter(user=request.user).select_related('coin')
    for item in watch_items:
        item.coin.latest_report = item.coin.reports.order_by('-calculated_at').first()

    return render(request, 'coins/watchlist.html', {'watch_items': watch_items})

def signup(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})