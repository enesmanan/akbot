import numpy as np
import pandas as pd
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score

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

    return model, X_test, y_test

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    print(f"R2 Score: {r2}")

    cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring='r2')
    print(f"Cross-validation R2 scores: {cv_scores}")
    print(f"Mean CV R2 score: {np.mean(cv_scores)}")

def predict_august_2024(model, df):
    unique_categories = df['İşlem Türü'].unique()
    unique_cities = df['Şehir'].unique()
    unique_subcategories = df['Harcama Kategorisi'].unique()

    august_predictions = []

    for category in unique_categories:
        for city in unique_cities:
            for subcategory in unique_subcategories:
                for day in range(1, 32):  
                    prediction_data = pd.DataFrame({
                        'Ay': [8],
                        'Yıl': [2024],
                        'Gün': [day],
                        'Haftanın_Günü': [(pd.Timestamp(2024, 8, day).dayofweek)],
                        'Ay_Sonu': [(day == 31)],
                        'İşlem Türü': [category],
                        'Şehir': [city],
                        'Harcama Kategorisi': [subcategory]
                    })
                    
                    try:
                        prediction = model.predict(prediction_data)
                        august_predictions.append({
                            'İşlem Türü': category,
                            'Şehir': city,
                            'Harcama Kategorisi': subcategory,
                            'Tutar': prediction[0]
                        })
                    except NotFittedError:
                        print(f"Model is not fitted for {category}, {city}, {subcategory}")

    return pd.DataFrame(august_predictions)

def visualize_results(predictions, save_path=None):
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
    
    plt.title('Ağustos 2024 İçin Tahmini Harcama Kategorileri Dağılımı', fontsize=16, fontweight='bold')
    
    total_spending = category_totals.sum()
    plt.text(0, 0, f'Toplam\n{total_spending:,.0f} TL', ha='center', va='center', fontsize=14, fontweight='bold')
    
    plt.axis('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path) 
        plt.close()  
    
    else:
        plt.show()

    print("\nTahmini Toplam Harcamalar:")
    for category, total in category_totals.items():
        print(f"{category}: {total:,.2f} TL")
    print(f"\nToplam Harcama: {total_spending:,.2f} TL")


def main():
    file_path = "Data/harcama_verisi.csv"
    df = load_and_preprocess_data(file_path)
    df = engineer_features(df)

    X = df.drop(['Tarih', 'Saat', 'Tutar'], axis=1)
    y = df['Tutar']

    model, X_test, y_test = create_and_train_model(X, y)
    evaluate_model(model, X_test, y_test)

    august_predictions = predict_august_2024(model, df)
    save_path = "exports/august_spending.png"  
    visualize_results(august_predictions, save_path)

if __name__ == "__main__":
    main()
