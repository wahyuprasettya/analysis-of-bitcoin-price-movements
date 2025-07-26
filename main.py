import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np

API_KEY = '1149bf39-b169-4962-aca8-b12068c8c77b'

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

    print(f"📊 Bitcoin price today ({today}): ${price:,.2f}")

    # Simpan ke CSV
    filename = 'btc_history.csv'
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'price'])

    if today not in df['date'].astype(str).values:
        new_row = pd.DataFrame([[today, price]], columns=['date', 'price'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(filename, index=False)
        print("✅ Today's data saved to CSV.")
    else:
        print("ℹ️ Today's data already exists.")

    # Analisis perbandingan harga dengan hari sebelumnya
    if len(df) >= 2:
        df = df.sort_values('date')
        previous_price = df.iloc[-2]['price']
        change = price - previous_price
        percent = (change / previous_price) * 100

        if change > 0:
            print(f"🚀 Increased by {percent:.2f}% since yesterday (${previous_price:,.2f})")
        elif change < 0:
            print(f"🔻 Decreased by {abs(percent):.2f}% since yesterday (${previous_price:,.2f})")
        else:
            print("⏸️ No change compared to yesterday.")

    # Ubah format tanggal dan urutkan
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Prediksi harga 1–3 tahun ke depan
    if len(df) >= 30:
        df['ordinal'] = df['date'].map(datetime.toordinal)
        X = df['ordinal'].values.reshape(-1, 1)
        y = df['price'].values

        model = LinearRegression()
        model.fit(X, y)

        print("\n📈 Prediksi harga Bitcoin ke depan (regresi linier):")
        future_years = [1, 2, 3]
        for year in future_years:
            future_date = df['date'].max() + pd.DateOffset(years=year)
            future_ordinal = np.array([[future_date.toordinal()]])
            future_price = model.predict(future_ordinal)[0]
            print(f"📅 Tahun +{year} ({future_date.date()}): ${future_price:,.2f}")

            # Tambahkan ke grafik
            plt.plot(future_date, future_price, 'ro')
            plt.text(future_date, future_price, f"${future_price:,.0f}", color='red')

    else:
        print("\nℹ️ Belum cukup data untuk prediksi (butuh ≥30 hari data).")

    # Buat grafik
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['price'], marker='o', linestyle='-', label='Harga Aktual')
    plt.title('Harga Harian Bitcoin & Prediksi')
    plt.xlabel('Tanggal')
    plt.ylabel('Harga (USD)')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.savefig("grafik.png")
    print("📊 Grafik disimpan sebagai 'grafik.png'")

else:
    print(f"❌ Failed to fetch data: {response.status_code} - {response.text}")