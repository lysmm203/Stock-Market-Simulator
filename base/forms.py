from django import forms



class StockParameterForm(forms.Form):
    money = forms.IntegerField()
    start_year = forms.IntegerField()
    end_year = forms.IntegerField()
 #   index = forms.CharField(widget=forms.Select(choices=stock_indices))

    # money = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # start_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2022)])
    # end_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2022)])
    # index = models.CharField(max_length=100)