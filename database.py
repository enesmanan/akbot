import sqlite3
import pandas as pd

class AkbotDatabase:
    def __init__(self, db_name='akbot.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Users tablosu
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Transactions tablosu
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date DATE NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """)

        # Campaigns tablosu
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Campaigns (
            campaign_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            start_date DATE,
            end_date DATE,
            conditions TEXT
        )
        """)

        # UserCampaigns tablosu
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserCampaigns (
            user_id INTEGER,
            campaign_id INTEGER,
            suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (campaign_id) REFERENCES Campaigns(campaign_id),
            PRIMARY KEY (user_id, campaign_id)
        )
        """)

        self.conn.commit()

    def add_user(self, username, email, password_hash):
        self.cursor.execute("""
        INSERT INTO Users (username, email, password_hash)
        VALUES (?, ?, ?)
        """, (username, email, password_hash))
        self.conn.commit()

    def add_transaction(self, user_id, date, amount, category, description):
        self.cursor.execute("""
        INSERT INTO Transactions (user_id, date, amount, category, description)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, date, amount, category, description))
        self.conn.commit()

    def get_user_transactions(self, user_id):
        query = """
        SELECT date, amount, category, description
        FROM Transactions
        WHERE user_id = ?
        ORDER BY date DESC
        """
        df = pd.read_sql_query(query, self.conn, params=(user_id,))
        return df

    def suggest_campaign(self, user_id, campaign_id):
        self.cursor.execute("""
        INSERT INTO UserCampaigns (user_id, campaign_id)
        VALUES (?, ?)
        """, (user_id, campaign_id))
        self.conn.commit()

    def get_user_campaigns(self, user_id):
        query = """
        SELECT c.name, c.description, uc.suggested_at, uc.accepted
        FROM UserCampaigns uc
        JOIN Campaigns c ON uc.campaign_id = c.campaign_id
        WHERE uc.user_id = ?
        """
        df = pd.read_sql_query(query, self.conn, params=(user_id,))
        return df

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = AkbotDatabase()

    db.add_user('enes_manan', 'efm@gmail.com', 'hashed_password')

    db.add_transaction(1, '2024-07-15', 100.50, 'Market', 'Haftalık alışveriş')

    transactions_df = db.get_user_transactions(1)
    print("Kullanıcı Harcamaları:")
    print(transactions_df)

    # db.add_campaign("Yaz İndirimi", "Tüm yaz ürünlerinde %20 indirim", "2024-06-01", "2024-08-31", "Minimum 100 TL alışveriş")

    #db.suggest_campaign(1, 1)
    campaigns_df = db.get_user_campaigns(1)
    print("\nKullanıcı Kampanyaları:")
    print(campaigns_df)

    db.close()