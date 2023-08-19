from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.list import ListView

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import StockParameters, StockTicker
from .forms import RegistrationForm, LoginForm, StockMarketParametersForm
from .utils import plot_stock_data, add_tickers_to_db, filter_stock_by_start_date, ticker_extractor, \
    create_plotting_df, calculate_investment_fluctuations, calculate_overall_stock_change

import requests
import yfinance as yf
from datetime import datetime
import time

class CustomLoginView(LoginView):
    """
    Class to render the registration page. Inherits from the LoginView.
    """
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    form_class = LoginForm
    authentication_form = LoginForm


    def get_success_url(self):
        """
        Redirects the user to the Stock Parameters page if login is successful.
        """
        return reverse_lazy('index')

class RegistrationView(CreateView):
    """
    Class to render the registration page. Inherits from the CreateView.
    """

    template_name = 'base/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Checks whether the registration is successful or not. If it is successful, login the user automatically.
        """
        valid_form = super().form_valid(form)
        login(self.request, self.object)
        return valid_form

class StockParameterFormView(LoginRequiredMixin, CreateView):
    """
    Class to render the Stock Parameter Form page. Inherits from the CreateView. Requires the user to be logged in
    to access the view.
    """
    template_name = 'base/stock_form.html'
    model = StockParameters

    form_class = StockMarketParametersForm
    success_url = reverse_lazy('index')

    def post(self, request):
        """
        After the user submits the form, save the inputs as session variables to be used in the subsequent views.
        Additionally, add all the tickers from the stocks.csv file into the database.
        """
        money = self.request.POST.get('money')
        start_date = self.request.POST.get('start_date')
        end_date = self.request.POST.get('end_date')
        index = self.request.POST.get('index')

        self.request.session['investment_amount'] = money
        self.request.session['money'] = money
        self.request.session['start_date'] = start_date
        self.request.session['end_date'] = end_date
        self.request.session['index'] = index
        self.request.session['portfolio'] = {}
        super(StockParameterFormView, self).post(request)
        add_tickers_to_db()


        return HttpResponseRedirect(f'/select/')


class StockSelectionView(LoginRequiredMixin, ListView):
    """
    Class to render the Stock Selection page. Inherits from the ListView. Requires the user to be logged in
    to access the view.
    """
    model = StockTicker
    template_name = 'base/stock_selection.html'
    context_object_name = 'stock_selection_data'

    def post(self, request):
        """
        After the user submits the form, the money left for investing as well as the user's current portfolio
        is updated. If the money is 0, the user is taken to the Results page. Otherwise, the user is redirected to the
        Stock Selection view.
        """
        chosen_stock = self.request.POST['chosen_stock']
        investment_amount = self.request.POST['investment_amount']
        stock_portfolio = self.request.session['portfolio']

        extracted_ticker = ticker_extractor(chosen_stock)
        stock_portfolio[extracted_ticker] = stock_portfolio.get(extracted_ticker, 0) + int(investment_amount)

        self.request.session['money'] = str(int(self.request.session['money']) - int(investment_amount))

        if int(self.request.session['money']) == 0:
            return HttpResponseRedirect(f'/results/')
        elif int(self.request.session['money']) > 0:
            return HttpResponseRedirect(self.request.path_info)
        else:
            self.request.session['money'] = str(int(self.request.session['money']) + int(investment_amount))
            return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        """
        Gets the start date input and uses that to filter out the list of stocks that are valid for that given
        timeframe. The filtered list of stocks are then saved as a session variable.
        """

        context = super().get_context_data(**kwargs)

        start_date = self.request.session['start_date']
        start_date_epoch = time.mktime(datetime.strptime(start_date, "%Y-%m-%d").timetuple())

        filtered_stocks = filter_stock_by_start_date(start_date_epoch)
        context['filtered_stocks'] = filtered_stocks
        self.request.session['filtered_stocks'] = filtered_stocks

        return context

class ResultsView(LoginRequiredMixin, ListView):
    """
    Class to render the RESULTS page. Inherits from the ListView. Requires the user to be logged in
    to access the view.
    """
    model = StockParameters
    context_object_name = 'user_input_data'
    template_name = 'base/results.html'

    def get_context_data(self, **kwargs):
        """
        Creates the graph and the data to be displayed in the Results page. The data is displayed in the form of a
        table.
        """
        context = super().get_context_data(**kwargs)


        start_date = self.request.session['start_date']
        end_date = self.request.session['end_date']
        index = self.request.session['index']
        stock_portfolio = self.request.session['portfolio']

        plotting_df = create_plotting_df(start_date, end_date, stock_portfolio, index)
        portfolio_historical_data = plotting_df['Portfolio Value'].values.tolist()
        index_historical_data = plotting_df['Index Value'].values.tolist()


        portfolio_result = calculate_overall_stock_change(portfolio_historical_data)
        index_result = calculate_overall_stock_change(index_historical_data)

        portfolio_df = plotting_df.iloc[:,4:]
        individual_stocks = []

        for col in portfolio_df:
            ticker = col
            stock_historical_data = portfolio_df[col].values.tolist()
            stock_result = calculate_overall_stock_change(stock_historical_data)
            individual_stocks.append([ticker,
                                     round(stock_historical_data[-1], 2),
                                     stock_result[1],
                                     stock_result[0]]
                                    )

        portfolio_vs_index_raw = plot_stock_data(plotting_df, index)
        portfolio_raw = plot_stock_data(plotting_df, index, portfolio_only=True)

        # The graphs
        context['portfolio_vs_index_raw'] = portfolio_vs_index_raw
        context['portfolio_raw'] = portfolio_raw

        # The data to be displayed
        context['portfolio_change'] = portfolio_result
        context['portfolio_value'] = round(portfolio_historical_data[-1], 2)

        context['index_change'] = index_result
        context['index_value'] = round(index_historical_data[-1], 2)

        context['individual_stocks'] = individual_stocks

        return context

# Define a function view that returns the stock tickers, rather than trying to overwrite StockSelectionView

def autocomplete_stock_list(request):
    """
    A function based view that returns the list of filtered stock tickers. This is used for the autocomplete
    functionality in the Stock Selection page.
    """
    if 'term' in request.GET:
        return JsonResponse(dict(request.session['filtered_stocks']))
    return render(request, 'base/autocomplete_stock_list.html')


