from django.urls import path
from .views import StockParameterFormView, StockSelectionView, ResultsView, autocomplete_stock_list, CustomLoginView, \
    RegistrationView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('', StockParameterFormView.as_view(), name='index'),
    path('select/', StockSelectionView.as_view(), name='select_stock'),
    path('results/', ResultsView.as_view(), name='results'),
    path('filtered_tickers/', autocomplete_stock_list, name='autocomplete')
]
