import pandas as pd

def analyze_spending(df):
    total_spending = df['Tutar'].sum()
    if total_spending > 10000:
        return "Yüksek harcama seviyeniz için size özel %10 indirimli kredi kartı teklifimiz var!"
    elif total_spending > 5000:
        return "Orta seviye harcamalarınız için %5 geri ödeme kampanyamızdan yararlanabilirsiniz!"
    else:
        return "Düşük harcama seviyeniz için faizsiz taksit kampanyamızı inceleyebilirsiniz!"

def get_campaign_suggestion(df):
    # Category-based spending analysis
    category_spending = df.groupby('Harcama Kategorisi')['Tutar'].sum()
    max_category = category_spending.idxmax()
    
    if max_category == 'Market':
        return f"En çok harcamanız {max_category} kategorisinde. Size özel market alışverişlerinizde %3 geri ödeme kampanyamız var!"
    elif max_category == 'Restoran':
        return f"En çok harcamanız {max_category} kategorisinde. Restoran harcamalarınızda 2 kat puan kazanma fırsatını kaçırmayın!"
    else:
        return f"En çok harcamanız {max_category} kategorisinde. Bu kategori için özel kampanyalarımızı incelemek ister misiniz?"

def handle_campaign_query_rule(df, query):
    if "kampanya" in query.lower() or "öneri" in query.lower():
        spending_analysis = analyze_spending(df)
        campaign_suggestion = get_campaign_suggestion(df)
        return f"{spending_analysis}\n\n{campaign_suggestion}"
    return None