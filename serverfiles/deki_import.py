import pandas as pd
import psycopg2
from datetime import datetime
from datetime import timedelta
from config.local import hostname

def update_deki():
    csv_file = 'kouteikanri/data/dekidaka.csv'
    df = pd.read_csv(csv_file, encoding='shift_jis')

    # データベースに接続
    conn = psycopg2.connect(
        host=hostname,
        port="5432",
        database="postgres",
        user="postgres",
        password="postgres"
    )

    # 対象の日付・便のデータを削除する
    # カーソルオブジェクトを作成
    dt = datetime.strftime(datetime.today(), "%Y/%m/%d")
    cur = conn.cursor()
    cur.execute("DELETE FROM kouteikanri_jisseki WHERE date = '" + dt + "';")
    # 変更をコミット
    conn.commit()
    # カーソルを閉じる
    cur.close()
    for index, row in df.iterrows():
        if row['チェーン名'] == 'ＬＷ惣菜':
            dt = datetime.strftime(datetime.today() + timedelta(days=1), "%Y/%m/%d")
            bn = 3
        else:
            dt = datetime.strftime(datetime.today(), "%Y/%m/%d")
            bn = row['便']
        if row['製造日'] == dt:
            # 区分
            if row['処理区分名称'] == '予測':
                kbn = '確定'
            else:
                kbn = str(row['処理区分名称'])
            # 担当者名
            if pd.notnull(row['担当者名']):
                tnt = "'" + str(row['担当者名']) + "'"
            else:
                tnt = 'NULL'
            # 指示量
            if pd.notnull(row['指示量']):
                shj = str(row['指示量'])
            else:
                shj = 'NULL'
            # 実績量
            if pd.notnull(row['実績量']):
                jsk = str(row['実績量'])
            else:
                jsk = 'NULL'
            # 加熱温度
            if pd.notnull(row['加熱温度']):
                knt = "'" + str(row['加熱温度']) + "'"
            else:
                knt = 'NULL'
            # 冷却温度
            if pd.notnull(row['冷却温度']):
                rky = "'" + str(row['冷却温度']) + "'"
            else:
                rky = 'NULL'
            # SQLクエリを実行
            # カーソルオブジェクトを作成
            cur = conn.cursor()
            cur.execute("INSERT INTO kouteikanri_jisseki(jigyousyo, date, bin, kakari, "
                        "kubun, hinban, shikakaricd, name, shiji, value, tanni, "
                        "tantou, hinonflg, kanetsu, reikyaku, minashiflg, tsukaflg, comp) "
                        "SELECT K.jigyousyo, K.date, K.bin, '" + row['係'] + "' AS kakari, '" +
                        kbn + "' AS kubun, K.hinban / 10, K.shikakaricd, K.name, " +
                        shj + " AS shiji, " + jsk + " AS value, tanni, " +
                        tnt + " AS tantou, " + str(row['品温測定フラグ']) + " AS hinonflg, " +
                        knt + " AS kanetsu, " + rky + " AS reikyaku, " +
                        str(row['みなし完了フラグ']) + " AS minashiflg, " +
                        str(row['追加指示完了フラグ']) + " AS tsukaflg, 0 "
                        "FROM kouteikanri_kouseihin AS K WHERE date >= '" + dt +
                        "' AND bin = " + str(bn) + " AND shikakaricd = " + str(row['品目コード']) + ";"
                        )
            # 変更をコミット
            conn.commit()
            # カーソルを閉じる
            cur.close()

    # Jissekiで出来高実績があればcomp=1にする
    # カーソルオブジェクトを作成
    cur = conn.cursor()
    cur.execute("UPDATE kouteikanri_jisseki SET comp = 1 WHERE date >= '" + dt +
                "' AND (value IS NOT NULL OR tantou = '指示完了' OR tsukaflg = 1);")
    # 変更をコミット
    conn.commit()
    # カーソルを閉じる
    cur.close()

    # =================================================================================
    # Processの製品を構成する仕掛品のcompが全て1ならset=1にする
    # =================================================================================
    # カーソルオブジェクトを作成
    cur = conn.cursor()
    cur.execute("SELECT * FROM kouteikanri_process WHERE date >= '" + dt +
                "' AND hinban IS NOT NULL AND set = 0;")
    for row in cur:
        print(str(row[5]) + "  " + row[8] + "  " + row[7])
        if str(row[4]) == 3:
            dp = 1
        else:
            dp = 0
        dd = datetime.strftime(row[3] + timedelta(days=dp), "%Y/%m/%d")
        cur0 = conn.cursor()
        cur0.execute("SELECT COUNT(*) FROM kouteikanri_jisseki WHERE date = '" + dd +
                     "' AND bin = " + str(row[4]) + " AND hinban = " + str(row[5]) +
                     " AND kubun = '" + str(row[7]) + "' AND comp = 1;")
        rows0 = cur0.fetchall()
        count0 = rows0[0][0]
        print("　完成: " + str(count0))
        cur0.close()
        # 1件以上完成した仕掛品がある場合
        if count0 >= 1:
            cur2 = conn.cursor()
            cur2.execute("SELECT COUNT(*) FROM kouteikanri_jisseki WHERE date = '" + dd +
                         "' AND bin = " + str(row[4]) + " AND hinban = " + str(row[5]) +
                         " AND kubun = '" + str(row[7]) + "' AND comp = 0;")
            rows = cur2.fetchall()
            count = rows[0][0]
            print("　未完成: " + str(count))
            # 未完成が0件なら完了
            if count == 0:
                cur3 = conn.cursor()
                cur3.execute("UPDATE kouteikanri_process SET set = 1 WHERE id = " + str(row[0]) + ";")
                print("　　全て完成したので完了にします")
                # 変更をコミット
                conn.commit()
                cur3.close()
            else:
                print("　　未完成があるため完了できません")
            # カーソルを閉じる
            cur2.close()
        # 1件も完成した仕掛品がない場合
        else:
            cur2 = conn.cursor()
            cur2.execute("SELECT COUNT(*) FROM kouteikanri_jisseki WHERE date = '" + dd +
                         "' AND bin = " + str(row[4]) + " AND hinban = " + str(row[5]) +
                         " AND kubun = '" + str(row[7]) + "';")
            rows = cur2.fetchall()
            count = rows[0][0]
            print("　仕掛品数: " + str(count))
            # 仕掛品数が0件なら完了にする
            # 全製品のデータがない場合も有効か？
            if count == 0:
                cur3 = conn.cursor()
                cur3.execute("UPDATE kouteikanri_process SET set = 1 WHERE id = " + str(row[0]) + ";")
                print("　　仕掛品がないため完了にします")
                # 変更をコミット
                conn.commit()
                cur3.close()
            else:
                print("　　未完成があるため完了できません")
            # カーソルを閉じる
            cur2.close()
    cur.close()
    # =================================================================================
