import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_KEY = 'YOUR_API_KEY_HERE'

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

params = {
    'symbol': 'BTC',
    'convert': 'USD'
}

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    price = data['data']['BTC']['quote']['USD']['price']
    today = datetime.now().strftime('%Y-%m-%d')

    print(f"Bitcoin price today ({today}): ${price:.2f}")

    # Save to CSV file
    filename = 'btc_history.csv'

    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'price'])

    if today not in df['date'].values:
        df = pd.concat([df, pd.DataFrame([[today, price]], columns=['date', 'price'])])
        df.to_csv(filename, index=False)
        print("Today's data saved to CSV.")
    else:
        print("Today's data already exists.")

    if len(df) >= 2:
        previous_price = df.iloc[-2]['price']
        change = price - previous_price
        percent = (change / previous_price) * 100

        if change > 0:
            print(f"🚀 Increased by {percent:.2f}% since yesterday (${previous_price:.2f})")
        elif change < 0:
            print(f"🔻 Decreased by {abs(percent):.2f}% since yesterday (${previous_price:.2f})")
        else:
            print("⏸️ No change compared to yesterday.")

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    plt.figure(figsize=(8, 4))
    plt.plot(df['date'], df['price'], marker='o', linestyle='-')
    plt.title('Bitcoin Daily Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

else:
    print(f"Failed to fetch data: {response.status_code} - {response.text}")
