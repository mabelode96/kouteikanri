import psycopg2

# データベースに接続
conn = psycopg2.connect(
  database="postgres",
  user="postgres",
  password="postgres",
  host="localhost",
  port="5432"
)

# カーソルオブジェクトを作成
cur = conn.cursor()
# SQLクエリを実行
cur.execute(
  "UPDATE kouteikanri_chouriproc SET startj = starty "
  "WHERE hinban < 1000 AND startj IS NULL AND starty <= CURRENT_TIMESTAMP;"
)
cur.execute(
  "UPDATE kouteikanri_chouriproc SET endj = endy, status = 1 "
  "WHERE hinban < 1000 AND endj IS NULL AND endy <= CURRENT_TIMESTAMP;"
)
# 変更をコミット
conn.commit()
# カーソルを閉じる
cur.close()
