import sqlite3

user_id = input('Введіть user_id, якого потрібно зробити адміністратором: ')
try:
    user_id = int(user_id)
except Exception:
    print('user_id має бути числом!')
    exit(1)

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('INSERT OR IGNORE INTO users (user_id, is_admin) VALUES (?, 1)', (user_id,))
c.execute('UPDATE users SET is_admin=1 WHERE user_id=?', (user_id,))
conn.commit()
conn.close()
print(f'User {user_id} тепер адміністратор!') 