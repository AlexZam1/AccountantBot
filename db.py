import sqlite3
import datetime


class BotDB:

    def __init__(self, db_file):
        # Создадим файл .db (создается автоматически).
        # За соединение будет отвечать переменная conn.
        self.conn = sqlite3.connect(db_file)
        # После создания объекта соединения с базой данных нужно создать объект cursor.
        # Он позволяет делать SQL-запросы к базе. Используем переменную cur для хранения объекта:
        self.cur = self.conn.cursor()

    def insert_db(self, name_spending, amount_spending, user_id, category_spending):
        """внесение записи в базу данных"""

        self.cur.execute("""CREATE TABLE IF NOT EXISTS spendings(
              expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              amount TEXT,
              categ TEXT,
              date TEXT,
              user_id INTEGER);
           """)
        self.conn.commit()

        date_spending = datetime.date.today()

        try:
            # определяет порядковый номер траты в столбце expense_id
            self.cur.execute("SELECT COUNT(*) FROM spendings")
            cur_id = self.cur.fetchone()[0] + 1
            self.conn.commit()
        except:
            cur_id = 1

        new_spending = (cur_id, name_spending, amount_spending, category_spending, date_spending, user_id)
        self.cur.execute("INSERT INTO spendings VALUES(?, ?, ?, ?, ?, ?);", new_spending)
        self.conn.commit()

    def treats_history(self, current_user_id):
        """возвращает данные по последним 7 тратам"""
        self.conn = sqlite3.connect('expense_table.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT *
            FROM spendings
            WHERE user_id={current_user_id}
            ORDER BY expense_id DESC
            LIMIT 7;""")
        last_spents = self.cur.fetchall()
        self.conn.commit()
        return last_spents

    def sum_history_expenses(self, current_user_id):
        """возвращает кортеж из строк с суммами трат по времени"""
        self.conn = sqlite3.connect('expense_table.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT SUM(amount) 
            FROM spendings
            WHERE user_id = {current_user_id}
            AND date = date('now','localtime');""")
        today_expenses = self.cur.fetchone()[0]
        self.conn.commit()

        self.cur.execute(f"""SELECT SUM(amount) 
            FROM spendings
            WHERE user_id={current_user_id}
            AND date=date('now','localtime', '-1 day','localtime');""")
        yesterday_expenses = self.cur.fetchone()[0]
        self.conn.commit()

        self.cur.execute(f"""SELECT SUM(amount) 
            FROM spendings
            WHERE user_id={current_user_id}
            AND date BETWEEN date('now', 'localtime', '-7 day', 'localtime') AND date('now', 'localtime');""")
        week_expenses = self.cur.fetchone()[0]
        self.conn.commit()

        self.cur.execute(f"""SELECT SUM(amount) 
            FROM spendings
            WHERE user_id={current_user_id}
            AND date BETWEEN date('now', 'localtime', '-1 month', 'localtime') AND date('now', 'localtime');""")
        month_expenses = self.cur.fetchone()[0]
        self.conn.commit()

        self.cur.execute(f"""SELECT SUM(amount) FROM spendings WHERE user_id={current_user_id};""")
        alltime_expenses = self.cur.fetchone()[0]
        self.conn.commit()

        return [today_expenses, yesterday_expenses, week_expenses, month_expenses, alltime_expenses]

    def sum_categ_expenses(self, current_user_id, categ):
        """возвращает строку с суммой трат для заданной категории"""
        self.conn = sqlite3.connect('expense_table.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT SUM(amount) FROM spendings WHERE user_id={current_user_id} AND categ=?;", (categ,))
        count_expenses = self.cur.fetchone()[0]
        self.conn.commit()

        if count_expenses:
            count_expenses = str(count_expenses) + " руб."
        else:
            count_expenses = "траты отсутствуют"

        return count_expenses
