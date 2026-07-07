from django.db import models
from model_utils import FieldTracker
from config.local import *

# 事業所, ライン名, 時間帯,製造日, 便,
# 品番, 単価, 区分, 製品名,
# 生産数h, 数量, 生産高, コンベア,
# 人員, パンミリ数, スライス枚数, スライス能力,
# 切替予定, 生産時間, 開始予定, 終了予定,
# 開始時間, 終了時間, 切替実績, 実際時間,
# status, set, fkey, comment


class Process(models.Model):
    jigyousyo = models.CharField('事業所', blank=True, max_length=50, default=jigyousyo)
    line = models.CharField('ライン名', blank=True, max_length=50)
    period = models.CharField('時間帯', blank=True, max_length=50)
    date = models.DateField('製造日', blank=True, null=True)
    bin = models.IntegerField('便', blank=True, null=True)
    hinban = models.IntegerField('品番', blank=True, null=True)
    price = models.FloatField('単価', blank=True, null=True)
    kubun = models.CharField('区分', blank=True, max_length=10)
    name = models.CharField('製品名', blank=True, max_length=50)
    seisanh = models.IntegerField('生産数h', blank=True, null=True)
    value = models.IntegerField('数量', blank=True, null=True)
    seisand = models.FloatField('生産高', blank=True, null=True)
    conveyor = models.FloatField('コンベア速度', blank=True, null=True)
    staff = models.IntegerField('人員', blank=True, null=True)
    panmm = models.CharField('パンミリ数', blank=True, max_length=50)
    slicev = models.IntegerField('スライス枚数', blank=True, null=True)
    slicep = models.IntegerField('スライス能力', blank=True, null=True)
    changey = models.IntegerField('切替予定', default=0, null=True)
    processy = models.IntegerField('生産時間', blank=True, null=True)
    starty = models.DateTimeField('開始予定', blank=True, null=True)
    endy = models.DateTimeField('終了予定', blank=True, null=True)
    startj = models.DateTimeField('開始時間', blank=True, null=True)
    endj = models.DateTimeField('終了時間', blank=True, null=True)
    changej = models.IntegerField('切替時間', blank=True, null=True)
    processj = models.IntegerField('実際時間', blank=True, null=True)
    staffj = models.IntegerField('実際人員', blank=True, null=True)
    status = models.IntegerField('status', default=0, null=True)
    set = models.IntegerField('set', default=0, null=True)
    setj = models.DateTimeField('準備時間', blank=True, null=True)
    comment = models.CharField('comment', blank=True, max_length=255)
    fkey = models.IntegerField('fkey', blank=True, null=True)

    tracker = FieldTracker()

    class Meta:
        db_table = 'kouteikanri_process'

    def __str__(self):
        return self.name


class Kouseihin(models.Model):
    jigyousyo = models.CharField('事業所', blank=True, max_length=50, default=jigyousyo)
    date = models.DateField('製造日', blank=True, null=True)
    bin = models.IntegerField('便', blank=True, null=True)
    kubun = models.CharField('区分', blank=True, max_length=50, null=True)
    hinban = models.IntegerField('品番', blank=True, null=True)
    shikakaricd = models.IntegerField('構成仕掛品CD', blank=True, null=True)
    name = models.CharField('構成仕掛品名', blank=True, max_length=50, null=True)
    value = models.FloatField('使用量', blank=True, null=True)
    tanni = models.CharField('単位', blank=True, max_length=50, null=True)
    comp = models.IntegerField('完了', blank=True, null=True)

    tracker = FieldTracker()

    class Meta:
        db_table = 'kouteikanri_kouseihin'

    def __str__(self):
        return self.name


# 製造日, チェーン名, 便, 係, 品目コード, 品目名称, 処理区分名称, 分割区分,
# 開始予定, 作業時間, 開始時刻, 締切予定, 終了時刻, 指示量, 実績量, 単位, 予実率,
# 担当者名, 回数, 調理開始時間, 機械名, 調理開始担当者名, 品温測定フラグ,
# 加熱測定日時, 加熱装置名称, 加熱温度, 時間, 塩素濃度, 浸漬時間, 担当者,
# 冷却測定日時, 冷却装置名称, 冷却温度, 修正フラグ, みなし完了フラグ, 追加指示完了フラグ
# ↓
# ↓
# 事業所, 製造日, 便, 係, 品目コード, 品目名称, 処理区分名称, 指示量, 実績量, 単位,
# 担当者名, 品温測定フラグ, 加熱温度, 冷却温度, みなし完了フラグ, 追加指示完了フラグ


class Jisseki(models.Model):
    jigyousyo = models.CharField('事業所', blank=True, max_length=50, default=jigyousyo)
    date = models.DateField('製造日', blank=True, null=True)
    bin = models.IntegerField('便', blank=True, null=True)
    kakari = models.CharField('係', blank=True, max_length=50, null=True)
    kubun = models.CharField('処理区分名称', blank=True, max_length=50, null=True)
    hinban = models.IntegerField('品番', blank=True, null=True)
    shikakaricd = models.IntegerField('品目コード', blank=True, null=True)
    name = models.CharField('品目名称', blank=True, max_length=50)
    shiji = models.FloatField('指示量', blank=True, null=True)
    value = models.FloatField('実績量', blank=True, null=True)
    tanni = models.CharField('単位', blank=True, max_length=50, null=True)
    tantou = models.CharField('担当者名', blank=True, max_length=50, null=True)
    hinonflg = models.IntegerField('品温測定フラグ', blank=True, null=True)
    kanetsu = models.CharField('加熱温度', blank=True, max_length=50, null=True)
    reikyaku = models.CharField('冷却温度', blank=True, max_length=50, null=True)
    minashiflg = models.IntegerField('みなし完了フラグ', blank=True, null=True)
    tsukaflg = models.IntegerField('追加指示完了フラグ', blank=True, null=True)
    comp = models.IntegerField('完了', blank=True, null=True)

    tracker = FieldTracker()

    class Meta:
        db_table = 'kouteikanri_jisseki'

    def __str__(self):
        return self.name
