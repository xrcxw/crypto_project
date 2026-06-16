from django.contrib import admin
from .models import Cryptocurrency, PriceHistory, VolatilityReport, Watchlist

@admin.register(Cryptocurrency)
class CryptoAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'current_price_usd', 'last_updated')
    search_fields = ('name', 'symbol')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('coin', 'timestamp', 'price_usd')
    list_filter = ('coin',)

@admin.register(VolatilityReport)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('coin', 'volatility_percent', 'price_change_percent', 'calculated_at')

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'coin', 'added_at')