import os
import shutil
import hashlib
import csvimport

n = [1, 2, 3, 4]
spath = ''
lpath = ''

for i in n:
  if i == 1:
    spath = '/mnt/nas0/生産実行システム/backup/出来高実績一覧表.csv'
    lpath = 'kouteikanri/data/dekidaka.csv'
  elif i == 2:
    spath = '/mnt/nas0/生産実行システム/backup/投入実績一覧表.csv'
    lpath = 'kouteikanri/data/tounyu.csv'
  elif i == 3:
    spath = '/mnt/nas0/原材料展開/csv/2303981【ＳＣＭ】ローソン２便確定/製品構成原材料データ.txt'
    lpath = 'kouteikanri/data/set2bin.txt'
  elif i == 4:
    spath = '/mnt/nas0/原材料展開/csv/2303983【ＳＣＭ】ローソン３便確定/製品構成原材料データ.txt'
    lpath = 'kouteikanri/data/set3bin.txt'

  if os.path.isfile(spath):
    if not os.path.isfile(lpath):
      shutil.copy(spath, lpath)
    else:
      with open(lpath,'rb') as lf:
        ldata = lf.read()
        lhash = hashlib.md5(ldata).hexdigest()
      with open(spath,'rb') as sf:
        sdata = sf.read()
        shash = hashlib.md5(sdata).hexdigest()
      #print(lhash, shash)
      if ldata != sdata:
        shutil.copy(spath, lpath)
        if i == 1:
          csvimport.update_deki()
