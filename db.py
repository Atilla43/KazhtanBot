import sqlite3

class Database:
  def __init__(self, db_url):
    self.conn = sqlite3.connect(db_url)
    self.cursor = self.conn.cursor()

    # Создание таблицы, если она еще не существует
    self.cursor.execute("""
      CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        full_name TEXT,
        adults INTEGER,
        children INTEGER,
        check TEXT,
        transfer TEXT
      )
    """)

  def save_data(self, user_id, first_name, data):
    """Сохраняет данные пользователя в базу данных"""
    self.cursor.execute(
      """
      INSERT OR REPLACE INTO user_data (
        user_id,
        first_name,
        full_name,
        adults,
        children,
        check,
        transfer
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
      """,
      (
        user_id,
        first_name,
        data["фио"],
        data["взрослые"],
        data["дети"],
        data["чек"],
        data["трансфер"],
      ),
    )
    self.conn.commit()

  def get_all_data(self):
    """Возвращает все данные из базы данных"""
    self.cursor.execute("SELECT * FROM user_data")
    return self.cursor.fetchall()

  def close(self):
    """Закрывает соединение с базой данных"""
    self.conn.close()

# Пример использования:
# db = Database("database.db")
# db.save_data(123456789, "Иван", {"фио": "Иванов Иван Иванович", "взрослые": 2, "дети": 1, "чек": "photo.jpg", "трансфер": "да"})
# data = db.get_all_data()
# print(data)
# db.close()
