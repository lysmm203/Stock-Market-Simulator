from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


stock_indices = [
    ('S&P 500', 'S&P 500'),
    ('DJIA', 'DJIA'),
    ('NASDAQ-100', 'NASDAQ')
]

# The attributes of each model (i.e. the classes StockParameters, StockAsset, and PriceHistory)
# represent a database field.

class StockParameters(models.Model):
    money = models.IntegerField(validators=[MinValueValidator(1)])
    start_date = models.DateField()
    end_date = models.DateField()
    index = models.CharField(max_length=100, choices=stock_indices, default='s&p')

    def __str__(self):
        return f"Money: {self.money}, Date Range: {self.start_date}-{self.end_date}, Index: {self.index}"

class StockTicker(models.Model):
    ticker = models.CharField(max_length=5)
    first_trade_date = models.IntegerField()
    company_name = models.CharField(max_length=255, default=None)

    def __str__(self):
        return f"Symbol: {self.ticker}, First Trade Date: {self.first_trade_date}, Company Name: {self.company_name}"
