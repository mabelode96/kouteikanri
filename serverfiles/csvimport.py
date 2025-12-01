import pandas as pd
from datetime import datetime
from datetime import timedelta
import psycopg2

csv_file = 'kouteikanri/data/dekidaka.csv'
df = pd.read_csv(csv_file, encoding='shift_jis')

# データベースに接続
conn = psycopg2.connect(
  database="postgres",
  user="postgres",
  password="postgres",
  host="localhost",
  port="5432"
)

for index, row in df.iterrows():
  # 自動更新から除外する係
  if row['係'] != 'オートフライヤー':
    if row['チェーン名'] == 'ＬＷ惣菜':
      dt = datetime.strftime(datetime.today() + timedelta(days=1), "%Y/%m/%d")
      bn = 3
    else:
      dt = datetime.strftime(datetime.today(), "%Y/%m/%d")
      bn = 2
    if row['製造日'] == dt and row['便'] == bn:
      # カーソルオブジェクトを作成
      cur = conn.cursor()
      # 区分
      if row['処理区分名称'] == '確定':
        kbn = "(kubun = '予測' OR kubun = '合算' OR kubun = '確定')"
      else:
        kbn = "kubun = '" + row['処理区分名称'] + "'"
      # 開始時間
      if row['調理開始時間'] == ''  or type(row['調理開始時間']) == float:
        s = 'startj = Null, '
      else:
        s = "startj = '" + str(row['調理開始時間']) + "', "
      # 終了時間
      if row['加熱測定日時'] == '' or type(row['加熱測定日時']) == float:
        if row['終了時刻'] == '' or type(row['終了時刻']) == float:
          e = "endj = Null "
        else:
          e = "endj = '" + str(row['終了時刻']) + "', status = 1 "
      else:
        e = "endj = '" + str(row['加熱測定日時']) + "', status = 1 "
      # SQLクエリを実行
      cur.execute("UPDATE kouteikanri_chouriproc SET " + s + e +
                  "WHERE name = '" + row['品目名称'] +
                  "' AND date = '" + dt + "' AND bin = " +
                  str(bn) + " AND " + kbn  + ";"
                  )
      # 変更をコミット
      conn.commit()
      # カーソルを閉じる
      cur.close()
