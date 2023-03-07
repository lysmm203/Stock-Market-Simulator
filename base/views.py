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
from .forms import RegistrationForm, LoginForm
from .utils import plot_stock_data, add_tickers_to_db, filter_stock_by_start_date, ticker_extractor, create_plotting_df

import requests
import yfinance as yf
from datetime import datetime
import time

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    form_class = LoginForm

    def get_success_url(self):
        return reverse_lazy('index')

class RegistrationView(CreateView):
    template_name = 'base/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')
    redirect_authenticated_user = True

    def form_valid(self, form):
        valid_form = super().form_valid(form)
        login(self.request, self.object)
        return valid_form

class StockParameterFormView(LoginRequiredMixin, CreateView):
    template_name = 'base/stock_form.html'
    model = StockParameters
    fields = '__all__'
    success_url = reverse_lazy('index')

    def post(self, request):
        money = self.request.POST.get('money')
        start_date = self.request.POST.get('start_date')
        end_date = self.request.POST.get('end_date')
        index = self.request.POST.get('index')

        self.request.session['money'] = money
        self.request.session['start_date'] = start_date
        self.request.session['end_date'] = end_date
        self.request.session['index'] = index
        self.request.session['portfolio'] = {}
        super(StockParameterFormView, self).post(request)
        print(f"Index chosen: {index}")
        add_tickers_to_db()

        return HttpResponseRedirect(f'/select/')


class StockSelectionView(LoginRequiredMixin, ListView):
    model = StockTicker
    template_name = 'base/stock_selection.html'
    context_object_name = 'stock_selection_data'
    # success_url = reverse_lazy('select', kwargs={'pk': 1})

    def post(self, request):
        chosen_stock = self.request.POST['chosen_stock']
        investment_amount = self.request.POST['investment_amount']
        stock_portfolio = self.request.session['portfolio']

        extracted_ticker = ticker_extractor(chosen_stock)
        stock_portfolio[extracted_ticker] = stock_portfolio.get(extracted_ticker, 0) + int(investment_amount)
        print(f"Current Portfolio: {stock_portfolio}")

        self.request.session['money'] = str(int(self.request.session['money']) - int(investment_amount))

        if self.request.session['money'] == '0':
            return HttpResponseRedirect(f'/results/')
        else:
            return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = self.request.session['start_date']
        start_date_epoch = time.mktime(datetime.strptime(start_date, "%Y-%m-%d").timetuple())

        filtered_stocks = filter_stock_by_start_date(start_date_epoch)
        context['filtered_stocks'] = filtered_stocks
        self.request.session['filtered_stocks'] = filtered_stocks

        return context

class ResultsView(LoginRequiredMixin, ListView):
    model = StockParameters
    context_object_name = 'user_input_data'
    template_name = 'base/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        start_date = self.request.session['start_date']
        end_date = self.request.session['end_date']
        index = self.request.session['index']
        stock_portfolio = self.request.session['portfolio']

        plotting_df = create_plotting_df(start_date, end_date, stock_portfolio, index)

        portfolio_vs_index_percentage = plot_stock_data(plotting_df, index, percentage=True)
        portfolio_percentage = plot_stock_data(plotting_df, index, portfolio_only=True, percentage=True)
        # portfolio_vs_index_raw = plot_stock_data(start_date, end_date, stock_portfolio, index)
        # portfolio_raw = plot_stock_data(start_date, end_date, stock_portfolio, index, portfolio_only=True)


        context['portfolio_vs_index_percentage'] = portfolio_vs_index_percentage
        context['portfolio_percentage'] = portfolio_percentage
        # context['portfolio_vs_index_raw'] = portfolio_vs_index_raw
        # context['portfolio_raw'] = portfolio_raw

        return context

# Define a function view that returns the stock tickers, rather than trying to overwrite StockSelectionView

def autocomplete_stock_list(request):
    if 'term' in request.GET:
        return JsonResponse(dict(request.session['filtered_stocks']))
    return render(request, 'base/autocomplete_stock_list.html')


