# Stock-Market-Simulator


## Description

<hr>

The stock market simulator is a Django web application that simulates the stock market
at different time periods. This application was created to be used as a resource for 
learning and experimenting with various investing strategies. By developing investment
strategies that work across various economic cycles, the user can learn to navigate through
the volatile stock market and create a stable, profitable portfolio.

## Setup

<hr>

This project was built using `python==3.10.8` and `Django==4.1.3`. As long 
as the Python version is compatible with the Django version used for this 
project, however, it should be sufficient. In addition to this, the user 
also needs to install the following modules:

- `appdirs==1.4.4`
- `asgiref==3.6.0`
- `beautifulsoup4==4.12.0`
- `certifi==2022.12.7`
- `cffi==1.15.1`
- `charset-normalizer==3.1.0`
- `contourpy==1.0.7`
- `cryptography==39.0.2`
- `cycler==0.11.0`
- `Django==4.1.3`
- `fonttools==4.39.2`
- `frozendict==2.3.5`
- `html5lib==1.1`
- `idna==3.4`
- `kiwisolver==1.4.4`
- `lxml==4.9.2`
- `matplotlib==3.7.1`
- `multitasking==0.0.11`
- `numpy==1.24.2`
- `packaging==23.0`
- `pandas==1.5.3`
- `Pillow==9.4.0`
- `pycparser==2.21`
- `pyparsing==3.0.9`
- `python-dateutil==2.8.2`
- `pytz==2022.7.1`
- `requests==2.28.2`
- `six==1.16.0`
- `soupsieve==2.4`
- `sqlparse==0.4.3`
- `urllib3==1.26.15`
- `webencodings==0.5.1`
- `yfinance==0.2.12`

These modules are also listed in the `requirements.txt` file, and can be 
installed at once by using the command `pip install -r requirements.txt`.
Assuming all the modules have been installed, the user can run three Django commands in the order displayed below

`python3 manage.py makemigrations`

`python3 manage.py migrate`

`python3 manage.py runserver` 

to setup and start the server. Assuming the server has 
started without any issues, the user can visit `https://127.0.0.1:8000` URL
to use the application. 


## Using the Application
<hr>

Once the user visits the `https://127.0.0.1:8000` URL, they are taken to the
Login page. In this page, the user can either login using the credentials they
used to register, or they can navigate to the Register page by pressing the Register button.
If the user successfully logs in, they are taken to the Stock Selection page. Otherwise,
an error message pops up and they will be unable to proceed. In order to use the application,
the user must be logged in. If they attempt to access other pages without being logged in,
they will be redirected to this page. 

![image](https://i.imgur.com/16wMUAd.png)


In the Register page, the user can create a new account to use the web application. If the 
user is able to register successfully, they will be automatically logged in and taken to the 
Stock Market Parameters page. 
![image](https://i.imgur.com/amvC6UQ.png)

In the Stock Market Parameters page, the user can set the setting for the stock market simulation.
The four parameters are Money, Start Date, End Date, and Index. The Money is the amount 
of money that the user will use to construct their portfolio. The Start and End Dates represent
the time period that the user will simulate, and the Index represents the stock market index 
that the user will choose as a benchmark for their portfolio. There are ranges that limit the amount of money the user 
can input, as well as for the start and end dates. The range of inputs that will be accepted for Money is from 1 to 
1000000, and the range of dates that will be accepted are from 9/30/1985 to the day before the date in which the 
application is run. 

![image](https://i.imgur.com/x1TGpK7.png)

Once the valid stock parameters have been set, the user is then taken to the Stock Selection page, where users can 
construct their portfolios. The input for Company has an autocomplete functionality for company names. For example, 
if the user inputs A, and Apple is a company that exists in that timeframe, it will appear as an option. It should 
be noted that users cannot invest beyond the amount of money left that is displayed in the screen. For example, if 
the amount of money left is $10000, they cannot invest $100000 into a company. 
Once the user has invested all of their money, they are taken to the Results page. 

![image](https://i.imgur.com/OSfuFVo.png)

In the Results page, a carousel consisting of two slides is shown to the user. In the first slide, the user
can see the performance of their portfolio pitted against that of the index they chose in the Stock Market
Parameters page. In the second slide, the user can see the constituents of their portfolio and assess their
individual performance. The user can choose to remain in the Results page or return to the Stock Market
Parameters page to run another simulation. 
![image](https://i.imgur.com/aX16ye2.png)
