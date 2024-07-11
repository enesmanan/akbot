Python bağımlılıklarını yükleyin

```
pip install -r requirements.txt
```

Mysql veritabanı ve kullanıcıyı oluşturun

```
mysql -u root -p
CREATE DATABASE cartdb;
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON cartdb.* TO 'newuser'@'localhost';
FLUSH PRIVILEGES;
```


Veri tabanı tablolarını oluşturun

```
python create_tables.py
```

Mysql komut satırına bağlan ve yeni kullanıcı ekle

```
mysql -u newuser -p cartdb
INSERT INTO User (username, balance) VALUES ('testuser', 1000.0);
```

Uygulamayı çalıştır

```
python3 app.py
```
