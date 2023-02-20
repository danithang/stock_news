import requests
import smtplib
from datetime import date, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
alpha_api = os.getenv("ALPHA_API")
news_api = os.getenv("NEWS_API")

my_email = "pythontestberry@gmail.com"
# password from app generator on gmail
password = os.getenv("PASSWORD")
other_email = "berrypythontest@yahoo.com"

# adding params aka the next part of the url in dictionary format
alpha_params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK_NAME,
    "outputsize": "compact",
    "apikey": alpha_api
}

response = requests.get(url=STOCK_ENDPOINT, params=alpha_params)
response.raise_for_status()
data = response.json()

# Get yesterday's closing stock price.
# Hint: You can perform list comprehensions on Python dictionaries.
# e.g. [new_value for (key, value) in dictionary.items()]
# Get the day before yesterday's closing stock price
today = date.today()
yesterday = str(today - timedelta(days=1))
before_yesterday = str(today - timedelta(days=2))

yesterday_data = float(data["Time Series (Daily)"][yesterday]["4. close"])
before_yesterday_data = float(data["Time Series (Daily)"][before_yesterday]["4. close"])

# getting the difference of yesterday's data and day before yesterday's data and if greater than 0 then it's up
# and less than 0 it's down
positive_diff = round(yesterday_data - before_yesterday_data, 2)
up_down = None
if positive_diff > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

# Work out the percentage difference in price between closing price yesterday and closing price the day
# before yesterday.
percentage_diff = round((positive_diff / before_yesterday_data) * 100, 2)

# If percentage is greater than 5, use the News API to get articles related to the COMPANY_NAME...
# getting the absolute value of percentage_diff which will be positive
if abs(percentage_diff) >= 5:
    news_params = {
        "apiKey": news_api,
        "q": COMPANY_NAME,
        "sortBy": "relevancy"
    }
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    # getting the articles key after parsing to json data
    news_data = news_response.json()["articles"]

    # Use Python slice operator to create a list that contains the first 3 articles.
    # Hint: https://stackoverflow.com/questions/509211/understanding-slice-notation
    # since articles is established in the news_data variable all it needs is a slice
    news = news_data[:3]

    # Create a new list of the first 3 article's headline and description using list comprehension.
    news_article = [f"{STOCK_NAME}: {up_down}{percentage_diff}%\nHeadline: {article['title']}."
                    f"\nBrief: {article['description']}" for article in news]

    # Send each article as a separate message via email.
    # taking each of the 3 articles and separating them into 3 different emails
    for article in news_article:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            # start transport layer security to secure the connection to the email server
            connection.starttls()
            # login process
            connection.login(user=my_email, password=password)
            # sending the email from one address to the other with message...adding subject and /n to make
            # sure it doesn't go into spam box...encode and decode takes away ascii errors
            connection.sendmail(from_addr=my_email, to_addrs=other_email,
                                msg=f"Subject: Tesla News\n\n{article.encode('ascii', 'ignore').decode('ascii')}")
