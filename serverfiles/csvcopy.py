import shutil
import hashlib

spath = '/mnt/nas0/生産実行システム/backup/投入実績一覧表.csv'
lpath = 'kouteikanri/data/tounyu.csv'
with open(lpath,'rb') as lf:
  ldata = lf.read()
  lhash = hashlib.md5(ldata).hexdigest()
with open(spath,'rb') as sf:
  sdata = sf.read()
  shash = hashlib.md5(sdata).hexdigest()
#print(lhash, shash)
if ldata != sdata:
  shutil.copy(spath, lpath)

spath = '/mnt/nas0/生産実行システム/backup/出来高実績一覧表.csv'
lpath = 'kouteikanri/data/dekidaka.csv'
with open(lpath,'rb') as lf:
  ldata = lf.read()
  lhash = hashlib.md5(ldata).hexdigest()
with open(spath,'rb') as sf:
  sdata = sf.read()
  shash = hashlib.md5(sdata).hexdigest()
#print(lhash, shash)
if ldata != sdata:
  shutil.copy(spath, lpath)
