from django.db import models


# ライン名,時間帯,製造日,便,
# 品番,単価,区分,製品名,
# 生産数h,数量,生産高,コンベア,
# 人員,パンミリ数,スライス枚数,スライス能力,
# 切替予定,生産時間,開始予定,終了予定,
# 開始時間,終了時間,切替実績,実際時間,
# status,set,fkey,comment


class Process(models.Model):
    line = models.CharField('ライン名', blank=True, max_length=50)
    period = models.CharField('時間帯', blank=True, max_length=50)
    date = models.DateField('製造日', blank=True)
    bin = models.IntegerField('便', blank=True)
    hinban = models.IntegerField('品番', blank=True)
    price = models.FloatField('単価', blank=True)
    kubun = models.CharField('区分', blank=True, max_length=10)
    name = models.CharField('製品名', blank=True, max_length=50)
    seisanh = models.IntegerField('生産数h', blank=True)
    value = models.IntegerField('数量', blank=True)
    seisand = models.FloatField('生産高', blank=True)
    conveyor = models.FloatField('コンベア速度', blank=True)
    staff = models.IntegerField('人員', blank=True)
    panmm = models.CharField('パンミリ数', blank=True, max_length=50)
    slicev = models.IntegerField('スライス枚数', blank=True)
    slicep = models.IntegerField('スライス能力', blank=True)
    changey = models.IntegerField('切替予定', blank=True)
    processy = models.IntegerField('生産時間', blank=True)
    starty = models.DateTimeField('開始予定', blank=True)
    endy = models.DateTimeField('終了予定', blank=True)
    startj = models.DateTimeField('開始時間', blank=True)
    endj = models.DateTimeField('終了時間', blank=True)
    changej = models.IntegerField('切替時間', blank=True)
    processj = models.IntegerField('実際時間', blank=True)
    status = models.IntegerField('status', default=0)
    set = models.IntegerField('set', default=0)
    setj = models.DateTimeField('準備時間', blank=True)
    fkey = models.CharField('fkey', blank=True, max_length=50)
    comment = models.CharField('comment', blank=True, max_length=255)

    class Meta:
        db_table = 'kouteikanri_process'

    def __str__(self):
        return self.name
