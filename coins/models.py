from django.db import models
from django.contrib.auth.models import User

class Cryptocurrency(models.Model):
    """Модель #1: информация о криптовалюте"""
    coin_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    current_price_usd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    market_cap = models.BigIntegerField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class PriceHistory(models.Model):
    """Модель #2: исторические цены"""
    coin = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='prices')
    timestamp = models.DateTimeField()
    price_usd = models.DecimalField(max_digits=20, decimal_places=2)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['coin', 'timestamp']
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.coin.symbol} - {self.timestamp.date()}: ${self.price_usd}"

class VolatilityReport(models.Model):
    """Модель #3: результаты анализа"""
    coin = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='reports')
    calculated_at = models.DateTimeField(auto_now_add=True)
    period_days = models.IntegerField(default=7)
    volatility_percent = models.DecimalField(max_digits=6, decimal_places=2)
    price_change_percent = models.DecimalField(max_digits=8, decimal_places=2)
    recommendation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.coin.symbol}: {self.volatility_percent}% ({self.period_days}д)"

class Watchlist(models.Model):
    """Модель #4: избранное пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'coin']