import random
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Turkish months mapping
turkish_months = {
    1: "Ocak",
    2: "Şubat",
    3: "Mart",
    4: "Nisan",
    5: "Mayıs",
    6: "Haziran",
    7: "Temmuz",
    8: "Ağustos",
    9: "Eylül",
    10: "Ekim",
    11: "Kasım",
    12: "Aralık"
}

years = [2024, 2023, 2022]
cities = ["İstanbul", "Ankara", "İzmir"]
transaction_types = ["Giyim", "Ulaşım", "Fatura", "Restoran"]
categories = {
    "Giyim": ["Zara", "H&M", "LC Waikiki"],
    "Ulaşım": ["Benzin", "Otobüs", "Taksi"],
    "Fatura": ["Elektrik", "Su", "İnternet"],
    "Restoran": ["Pizza", "Kebap", "Fast Food"]
}

def generate_data(num_records):
    data = {
        "Yıl": [],
        "Ay": [],
        "Gün": [],
        "Tarih": [],
        "Saat": [],
        "İşlem Türü": [],
        "Harcama Kategorisi": [],
        "Şehir": [],
        "Tutar": []
    }

    # Ensure each month has one bill
    bill_days = {}
    for year in years:
        for month in range(1, 13):
            bill_days[(year, month)] = random.randint(1, 28)

    for _ in range(num_records):
        year = random.choice(years)
        if year == 2024:
            month = random.randint(1, 7)  # Only generate data up to July 2024
        else:
            month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe choice for day
        date = datetime(year, month, day)
        time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"  # HH:MM format

        transaction_type = random.choice(transaction_types)
        category = random.choice(categories[transaction_type])
        city = random.choice(cities)

        # Determine the amount based on category and ensure bills increase yearly
        if transaction_type == "Giyim":
            amount = round(random.uniform(50, 1000), 2)
        elif transaction_type == "Ulaşım":
            if category == "Benzin":
                time = f"{random.randint(11, 13):02}:{random.randint(0, 59):02}"  # Between 11:00 and 13:59
            amount = round(random.uniform(10, 500), 2)
        elif transaction_type == "Fatura":
            day = bill_days[(year, month)]
            base_amount = {"Elektrik": 100, "Su": 50, "İnternet": 80}
            amount = round(base_amount[category] * (1 + 0.05 * (2024 - year)), 2)
        elif transaction_type == "Restoran":
            if category in ["Pizza", "Kebap", "Fast Food"]:
                time = f"{random.randint(12, 14):02}:{random.randint(0, 59):02}"  # Between 12:00 and 14:59
            amount = round(random.uniform(20, 200), 2)

        data["Yıl"].append(year)
        data["Ay"].append(turkish_months[month])  # Adding Turkish month names
        data["Gün"].append(day)
        data["Tarih"].append(date.strftime("%Y-%m-%d"))
        data["Saat"].append(time)
        data["İşlem Türü"].append(transaction_type)
        data["Harcama Kategorisi"].append(category)
        data["Şehir"].append(city)
        data["Tutar"].append(amount)

    return pd.DataFrame(data)

# Generate 1000 records
df = generate_data(2000)

# Save to CSV
df.to_csv("harcama_verisi.csv", index=False)

# Grouping by 'Harcama Kategorisi' and summing 'Tutar'
grouped_df = df.groupby('Harcama Kategorisi')['Tutar'].sum()

# Plotting the pie chart
plt.figure(figsize=(10, 7))
grouped_df.plot(kind='pie', autopct='%1.1f%%')
plt.title('Harcama Kategorilerine Göre Toplam Tutar Dağılımı')
plt.ylabel('')  # Hiding the y-label
plt.show()

print("Veri oluşturuldu ve 'harcama_verisi.csv' dosyasına kaydedildi!")
