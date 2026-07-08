import pandas as pd
import psycopg2
from datetime import datetime
from datetime import timedelta
from config.local import hostname
from config.local import jigyousyo

def update_kouseihin(s):
    if s == '3':
        csv_file = 'data/lw2y.txt'
        kb = '予測'
    elif s == '4':
        csv_file = 'data/lw2k.txt'
        kb = '確定'
    elif s == '5':
        csv_file = 'data/lw3y.txt'
        kb = '予測'
    elif s == '6':
        csv_file = 'data/lw3k.txt'
        kb = '確定'
    elif s == '7':
        csv_file = 'data/cd1k.txt'
        kb = '確定'
    else: #ローカルテスト用
        csv_file = 'data/製品構成原材料データ.txt'
        kb = '確定'

    with open(csv_file, 'r', encoding='cp932') as f:
        lines = f.readlines()
        target_line = lines[0].split('\t')
        dt = datetime.strptime(target_line[3], "%Y%m%d").date()
        dt = datetime.strftime(dt + timedelta(days=0), "%Y/%m/%d")
        f.close()

    csv_column = ['nu1', 'nu2', 'nu3', 'hinban', 'nu4', 'bin', 'nu5', 'shikakaricd', 'name',
                  'nu6', 'nu7', 'nu8', 'nu9', 'nu10', 'value', 'tanni', 'nu11',
                  'nu12', 'nu13', 'nu14', 'nu15', 'nu16', 'nu17', 'nu18', 'nu19', 'nu20']

    df = pd.read_csv(csv_file, sep='\t', encoding='cp932', header=None, skiprows=[0], names=csv_column)
    bn = df.iloc[0, 5]

    # データベースに接続
    conn = psycopg2.connect(
        host=hostname,
        port="5432",
        database="postgres",
        user="postgres",
        password="postgres"
    )

    # カーソルオブジェクトを作成
    cur = conn.cursor()
    # 対象の日付・便のデータを削除する
    cur.execute("DELETE FROM kouteikanri_kouseihin "
                "WHERE date = '" + dt + "' AND bin = " + str(bn) + ";"
                )
    # 変更をコミット
    conn.commit()

    for index, row in df.iterrows():
        # レコードを追加
        cur.execute("INSERT INTO kouteikanri_kouseihin(jigyousyo, date,"
                    "bin, kubun, hinban, shikakaricd, name, value, tanni, comp) "
                    "SELECT '" + jigyousyo + "', '" + dt + "', " +
                    str(row['bin']) + ",' " + kb + "', " + str(row['hinban']) + ", " +
                    str(row['shikakaricd']) + ", '" + row['name'] + "', " +
                    str(row['value']) + ", '" + row['tanni'] + "', 0;"
                    )
        # 変更をコミット
        conn.commit()

    # カーソルを閉じる
    cur.close()
