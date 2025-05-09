from django.db import models
from config.local import *


# 事業所, 順番, 品目コード, 品目名称, 予測生産, 処理区分名称, 指示量, 単位,
# 調理種別, バッチ当り出来高, バッチ当り調理時間, 1時間当り出来高, 切替時間, 回数,
# 作業時間, 開始時間, 終了時間, 開始時刻, 締切予定, 終了時刻, status

class Process(models.Model):
    jigyousyo = models.CharField('事業所', blank=True, max_length=50, default=jigyousyo)
    line = models.CharField('ライン名', blank=True, max_length=50)
    period = models.CharField('時間帯', blank=True, max_length=50)
    date = models.DateField('製造日', blank=True)
    bin = models.IntegerField('便', blank=True)
    number = models.IntegerField('順番', blank=True, null=True)
    hinban = models.IntegerField('品目コード', blank=True, null=True)
    name = models.CharField('品目名称', blank=True, null=True, max_length=50)
    yosoku = models.IntegerField('予測生産', blank=True, null=True)
    kubun = models.CharField('処理区分名称', blank=True, null=True, max_length=10)
    value = models.FloatField('指示量', blank=True, null=True)
    unit = models.CharField('単位', blank=True, null=True, max_length=10)
    ctype = models.CharField('調理種別', blank=True, null=True, max_length=10)
    batdeki = models.FloatField('バッチ当り出来高', blank=True, null=True)
    battime = models.IntegerField('バッチ当り調理時間', blank=True, null=True)
    hdeki = models.FloatField('1時間当り出来高', blank=True, null=True)
    changey = models.IntegerField('切替予定', default=0)
    batcount = models.IntegerField('回数', default=1)
    processy = models.IntegerField('作業時間', blank=True, null=True)
    starty = models.DateTimeField('開始予定', blank=True, null=True)
    endy = models.DateTimeField('終了予定', blank=True, null=True)
    startj = models.DateTimeField('開始時刻', blank=True, null=True)
    shimej = models.DateTimeField('締切時間', blank=True, null=True)
    endj = models.DateTimeField('終了時刻', null=True)
    changej = models.IntegerField('切替時間', blank=True, null=True)
    processj = models.IntegerField('作業時間', blank=True, null=True)
    status = models.IntegerField('status', default=0)

    class Meta:
        db_table = 'kouteikanri_chouriproc'

    def __str__(self):
        return self.name
