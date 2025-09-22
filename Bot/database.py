import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def set_nickname(self, user_id, nickname):
        with self.connection:
            return self.cursor.execute("UPDATE users SET nickname = ? WHERE user_id = ?", (nickname, user_id))

    def get_signup(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT signup FROM users WHERE user_id = ?", (user_id,)).fetchall()
            for row in result:
                signup = str(row[0])
            return signup

    def set_signup(self, user_id, signup):
        with self.connection:
            return self.cursor.execute("UPDATE users SET signup = ? WHERE user_id = ?", (signup, user_id))

    def get_nickname(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT nickname FROM users WHERE user_id = ?", (user_id,)).fetchall()
            for row in result:
                nickname = str(row[0])
            return nickname

    def get_balance(self, user_id):
        balance = self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return int(float(balance[0]))

    def add_balance(self, user_id, amount: int):
        with self.connection:
            new_balance = int(self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]) + amount
            return self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))

    def min_balance(self, user_id, amount: int):
        with self.connection:
            new_balance = int(float(self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])) - amount
            if new_balance >= 0:
                return self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            else:
                raise Exception

    def set_bet(self, user_id, bet):
        with self.connection:
            if bet <= self.get_balance(user_id):
                return self.cursor.execute("UPDATE users SET bet = ? WHERE user_id = ?", (bet, user_id))
            else:
                raise Exception

    def get_users_info(self):
        with self.connection:
            return [(user, balance) for user, balance in self.cursor.execute('SELECT nickname, balance FROM users').fetchall()]

    def get_users_id(self):
        with self.connection:
            return [user_id[0] for user_id in self.cursor.execute('SELECT user_id FROM users').fetchall()]

    def get_bet(self, user_id):
        return int(self.cursor.execute("SELECT bet FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])

    def get_played(self, user_id):
        return int(self.cursor.execute("SELECT played FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])

    def get_win(self, user_id):
        return int(self.cursor.execute("SELECT win FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])

    def get_lose(self, user_id):
        return int(self.cursor.execute("SELECT lose FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])

    def add_played(self, user_id):
        with self.connection:
            played = int(self.cursor.execute("SELECT played FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]) + 1
            return self.cursor.execute("UPDATE users SET played = ? WHERE user_id = ?", (played, user_id))

    def add_win(self, user_id):
        with self.connection:
            win = int(self.cursor.execute("SELECT win FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]) + 1
            return self.cursor.execute("UPDATE users SET win = ? WHERE user_id = ?", (win, user_id))

    def add_lose(self, user_id):
        with self.connection:
            lose = int(self.cursor.execute("SELECT lose FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]) + 1
            return self.cursor.execute("UPDATE users SET lose = ? WHERE user_id = ?", (lose, user_id))

    def get_id_by_nickname(self, nickname):
        with self.connection:
            user_id = self.cursor.execute("SELECT user_id FROM users WHERE nickname = ?", (nickname,)).fetchone()[0]
            if user_id:
                return user_id
            else:
                raise Exception



