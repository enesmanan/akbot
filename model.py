import os
import pickle
import pandas as pd
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df['Tarih'] = pd.to_datetime(df['Tarih'])
    df['Ay'] = df['Tarih'].dt.month
    df['Yıl'] = df['Tarih'].dt.year
    return df

def engineer_features(df):
    df['Gün'] = df['Tarih'].dt.day
    df['Haftanın_Günü'] = df['Tarih'].dt.dayofweek
    df['Ay_Sonu'] = (df['Tarih'].dt.is_month_end).astype(int)
    return df

def create_and_train_model(X, y):
    categorical_features = ['İşlem Türü', 'Şehir', 'Harcama Kategorisi']
    numeric_features = ['Ay', 'Yıl', 'Gün', 'Haftanın_Günü', 'Ay_Sonu']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', SimpleImputer(strategy='median'), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    return model

def save_model(model, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(model, file)

def load_model(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)

def predict_next_month(model, df, year, month):
    unique_categories = df['İşlem Türü'].unique()
    unique_cities = df['Şehir'].unique()
    unique_subcategories = df['Harcama Kategorisi'].unique()

    predictions = []

    for category in unique_categories:
        for city in unique_cities:
            for subcategory in unique_subcategories:
                for day in range(1, 32):  
                    prediction_data = pd.DataFrame({
                        'Ay': [month],
                        'Yıl': [year],
                        'Gün': [day],
                        'Haftanın_Günü': [(pd.Timestamp(year, month, day).dayofweek)],
                        'Ay_Sonu': [(day == pd.Timestamp(year, month, day).days_in_month)],
                        'İşlem Türü': [category],
                        'Şehir': [city],
                        'Harcama Kategorisi': [subcategory]
                    })
                    
                    prediction = model.predict(prediction_data)
                    predictions.append({
                        'İşlem Türü': category,
                        'Şehir': city,
                        'Harcama Kategorisi': subcategory,
                        'Tutar': prediction[0]
                    })

    return pd.DataFrame(predictions)

def visualize_results(predictions, save_path):
    category_totals = predictions.groupby('İşlem Türü')['Tutar'].sum()
    
    red_palette = sns.color_palette("Reds", n_colors=len(category_totals))
    
    plt.figure(figsize=(14, 10))
    wedges, texts, autotexts = plt.pie(category_totals, 
                                        labels=category_totals.index, 
                                        autopct='%1.1f%%',
                                        colors=red_palette,
                                        startangle=90,
                                        pctdistance=0.85)
    
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.setp(autotexts, size=10, weight="bold", color="white")
    plt.setp(texts, size=12)
    
    plt.title('Gelecek Ay İçin Tahmini Harcama Kategorileri Dağılımı', fontsize=16, fontweight='bold')
    
    total_spending = category_totals.sum()
    plt.text(0, 0, f'Toplam\n{total_spending:,.0f} TL', ha='center', va='center', fontsize=14, fontweight='bold')
    
    plt.axis('equal')
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    plt.close()
    
    return save_path, category_totals, total_spending

def main():
    file_path = "Data/harcama_verisi.csv"
    df = load_and_preprocess_data(file_path)
    df = engineer_features(df)

    X = df.drop(['Tarih', 'Saat', 'Tutar'], axis=1)
    y = df['Tutar']

    model = create_and_train_model(X, y)
    save_model(model, "model.pkl")

if __name__ == "__main__":
    main()