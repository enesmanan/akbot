import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def analyze_spending(df):
    total_spending = df['Tutar'].sum()
    category_spending = df.groupby('Harcama Kategorisi')['Tutar'].sum().to_dict()
    top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return total_spending, category_spending, top_categories

def generate_campaign_suggestion(total_spending, category_spending, top_categories):
    prompt = f"""
    Bir banka müşterisi için kişiselleştirilmiş kampanya önerisi oluştur. Müşteri bilgileri:

    - Toplam harcama: {total_spending:.2f} TL
    - Kategori bazlı harcamalar: {category_spending}
    - En çok harcama yapılan 3 kategori: {top_categories}

    Bu bilgileri kullanarak:
    1. Müşterinin harcama alışkanlıklarını kısaca analiz et.
    2. Toplam harcama miktarına ve harcama kategorilerine uygun 2 özel kampanya veya kredi teklifi öner.
    3. Her kampanya veya kredi için kısa bir açıklama ve avantajlarını belirt.

    Cevabı Türkçe olarak, samimi ve ikna edici bir dille yaz. Öneriler gerçekçi ve banka müşterisine değer katacak nitelikte olmalı.
    Müşteriye cevabı onu düşündüğünü hissettirecek şekilde sun.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir banka müşteri temsilcisisin. Müşterilere özel kampanya ve kredi önerileri sunuyorsun."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content

def handle_campaign_query(df, query):
    if "kampanya" in query.lower() or "öneri" in query.lower() or "teklif" in query.lower():
        total_spending, category_spending, top_categories = analyze_spending(df)
        campaign_suggestion = generate_campaign_suggestion(total_spending, category_spending, top_categories)
        return campaign_suggestion
    return None