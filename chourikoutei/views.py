import datetime
import psycopg2
from io import StringIO
from config.local import *
from django.db.models import Q, Count, Max, Sum, Case, When, F
from django.db.models.functions import Abs
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .forms import MyModelForm, KouteiEditForm, PeriodsChoiceForm
from .models import Process, Jisseki, Tounyu
import plotly.express as px
import pandas as pd
from django.views.generic import TemplateView
from django_pandas.io import read_frame


# 検索
def top(request):
    # 初期値を設定
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    f1 = MyModelForm(initial={'date': d, 'period': '昼勤'})
    f2 = PeriodsChoiceForm(initial={'period': '昼勤'})
    return render(request, 'top2.html', {'form1': f1, 'form2': f2})


# リダイレクト用
def redirect_b(request):
    if request.method == 'POST':
        date = request.POST['date']
        period = request.POST['period']
        return render(request, 'redirect2.html', {'date': date, 'period': period})


# 各種実績
class JissekiView(ListView):
    model = Jisseki
    context_object_name = 'jisseki'
    template_name = 'results.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['select'] = self.kwargs['select']
        ctx['datef'] =self.kwargs['date']
        ctx['periodf'] = self.kwargs['period']
        return ctx

    def get_queryset(self, **kwargs):
        if self.kwargs['period'] == '夜勤':
            dt = datetime.datetime.strptime(self.kwargs['date'], '%Y-%m-%d')
            d = dt.strftime('%Y/%m/%d')
            b0 = 3
            b1 = 3
        else:
            dt = datetime.datetime.strptime(self.kwargs['date'], '%Y-%m-%d')
            d = dt.strftime('%Y/%m/%d')
            b0 = 1
            b1 = 2
        select = self.kwargs['select']
        if select == '1':
            get_tounyu()
            return Tounyu.objects.filter(
                Q(jisseki__isnull=True) &
                Q(date__exact=d) &
                Q(bin__gte=b0) &
                Q(bin__lte=b1) &
                ~Q(line__exact='炊飯') &
                ~Q(tantou__exact='指示完了') &
                ~Q(kanryouflg__exact=1)
            ).all().order_by('line', 'hinban')
        elif select == '2':
            get_dekidaka()
            return Jisseki.objects.filter(
                Q(jisseki__isnull=True) &
                Q(date__exact=d) &
                Q(bin__gte=b0) &
                Q(bin__lte=b1) &
                ~Q(tantou__exact='指示完了') &
                ~Q(kanryouflg__exact=1)
            ).all().order_by('line', 'hinban')
        elif select == '3':
            get_dekidaka()
            return Jisseki.objects.filter(
                (Q(kanetsu__isnull=True) | Q(kanetsu__exact='')) &
                (Q(hinonflg__exact=1) | Q(hinonflg__exact=3)) &
                Q(date__exact=d) &
                Q(bin__gte=b0) &
                Q(bin__lte=b1) &
                ~Q(tantou__exact='指示完了') &
                ~Q(kanryouflg__exact=1)
            ).all().order_by('line', 'hinban')
        elif select == '4':
            get_dekidaka()
            return Jisseki.objects.filter(
                Q(reikyaku__isnull=True) &
                (Q(hinonflg__exact=2) | Q(hinonflg__exact=3)) &
                Q(date__exact=d) &
                Q(bin__gte=b0) &
                Q(bin__lte=b1) &
                ~Q(tantou__exact='指示完了') &
                ~Q(kanryouflg__exact=1)
            ).all().order_by('line', 'hinban')
        else:
            return Jisseki.objects.all().order_by('line', 'hinban')


# 調理工程 全ライン一覧
class ListAll(ListView):
    model = Process
    context_object_name = 'data'
    template_name = 'list_all.html'
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    form = MyModelForm(initial={'date': d, 'period': '昼勤'})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['date'] = self.kwargs['date']
        ctx['period'] = self.kwargs['period']
        return ctx

    def get_queryset(self, **kwargs):
        p = self.kwargs['period']
        s = self.kwargs['date'] + " 0:00:00+09"
        e = self.kwargs['date'] + " 23:59:59+09"

        tstr = self.kwargs['date']
        tdata = datetime.datetime.strptime(tstr, '%Y-%m-%d')

        return Process.objects.filter(starty__gte=s, starty__lte=e, period__exact=p) \
            .values("line", "period") \
            .annotate(all_cnt=Count("hinban"),
                      end_cnt=Count("endj"),
                      left_cnt=Count("hinban") - Count("endj"),
                      progress=Count("endj") * 100 / Count("hinban"),
                      left_time=Sum("changey") - Sum(Abs(F("status") * F("changey"))) +
                                Sum("processy") - Sum(Abs(F("status") * F("processy"))),
                      endy_max=Max("endy"),
                      endj_max=Max("endj"),
                      comp_time=Max("endy")
                      )

    @staticmethod
    def post(request):
        date = request.POST['date']
        period = request.POST['period']
        return render(request, 'chourikoutei:list_all',
                      {'date': date, 'period': period}
                      )

# 調理工程
class List(ListView):
    model = Process
    context_object_name = 'kouteis'
    template_name = 'list2.html'
    paginate_by = 8
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    form = MyModelForm(initial={'date': d, 'period': '昼勤'})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ln = self.kwargs['line']
        dt = self.kwargs['date']
        pr = self.kwargs['period']
        ql = Q(line__exact=ln)
        qd = Q(date__exact=dt)
        qp = Q(period__exact=pr)
        qs = Q(status__exact=1)
        # ライン名 ========================================================================
        ctx['linef'] = self.kwargs['line']
        # 製造日 ==========================================================================
        tstr = self.kwargs['date']
        tdata = datetime.datetime.strptime(tstr, '%Y-%m-%d')
        tdate = str(tdata.year) + '年' + str(tdata.month) + '月' + str(tdata.day) + '日'
        ctx['datef'] = tdate
        # 時間帯 ==========================================================================
        ctx['periodf'] = self.kwargs['period']
        # 終了予定 ========================================================================
        ctx['maxendy'] = endy_max(ln, dt, pr)
        # 終了数/総数 ======================================================================
        ctx['all_cnt'] = all_cnt(ctx['linef'], tdata, ctx['periodf'])
        ctx['comp_cnt'] = comp_cnt(ctx['linef'], tdata, ctx['periodf'])
        # 残り時間 ========================================================================
        ctx['left_time'] = left_minute(ctx['linef'], tdata, ctx['periodf'])
        # 終了予測 =========================================================================
        ctx['comptime'] = comp_time(ln, dt, pr)
        # 進捗 ============================================================================
        if endy_max(ln, dt, pr) is None:
            progress = 0
        else:
            progress = get_stime(comp_time(ln, dt, pr), endy_max(ln, dt, pr))
        ctx['progress'] = progress
        ctx["new_date"] = datetime.datetime.now()
        # 進捗率 ==========================================================================
        ctx['progress_p'] = comp_prog(ctx['linef'], tdata, ctx['periodf'])
        ctx['jissekiauto'] = jissekiauto
        # plotly
        ctx["plot"] = line_charts(dt, pr, ln)
        return ctx

    def get_queryset(self, **kwargs):
        return (Process.objects.all().order_by('endj', 'startj', 'starty')
        .filter(
            Q(starty__gte=self.kwargs['date'] + ' 0:00:00+09') &
            Q(starty__lte=self.kwargs['date'] + ' 23:59:59+09') &
            Q(period__exact=self.kwargs['period']) &
            Q(line__exact=self.kwargs['line']) &
            Q(hinban__gt=0))
        )

    @staticmethod
    def post(request):
        date = request.POST['date']
        period = request.POST['period']
        line = request.POST['line']
        return render(request, 'chourikoutei:list',
                      context={'date': date, 'period': period, 'line': line})


# 「終了予定」を取得する関数
def endy_max(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) &
        Q(date__exact=date) &
        Q(period__exact=period)
    )
    if koutei.count() == 0:
        return None
    else:
        ym = koutei.aggregate(Max('endy'))
        if ym['endy__max'] is None:
            return None
        else:
            return ym['endy__max'].astimezone()


# 「終了実績」を取得する関数
def endj_max(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) &
        Q(date__exact=date) &
        Q(period__exact=period)
    )
    if koutei.count() == 0:
        return None
    else:
        jm = koutei.aggregate(Max('endj'))
        if jm['endj__max'] is None:
            return None
        else:
            return jm['endj__max'].astimezone()


# 「残り生産時間」を計算する関数
def left_time(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) &
        Q(date__exact=date) &
        Q(period__exact=period) &
        Q(status__exact=0)
    )
    sum_py = koutei.aggregate(Sum('processy'))
    if sum_py['processy__sum'] is None:
        py = 0
    else:
        py = sum_py['processy__sum']
    sum_cy = koutei.aggregate(Sum('changey'))
    if sum_cy['changey__sum'] is None:
        cy = 0
    else:
        cy = sum_cy['changey__sum']
    tt = py + cy
    return datetime.timedelta(minutes=tt)


# 「残り生産時間(分)」を計算する関数
def left_minute(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) &
        Q(date__exact=date) &
        Q(period__exact=period) &
        Q(status__exact=0)
    )
    sum_py = koutei.aggregate(Sum('processy'))
    if sum_py['processy__sum'] is None:
        py = 0
    else:
        py = sum_py['processy__sum']
    sum_cy = koutei.aggregate(Sum('changey'))
    if sum_cy['changey__sum'] is None:
        cy = 0
    else:
        cy = sum_cy['changey__sum']
    tt = py + cy
    return tt


# 「終了予測」を計算する関数
def comp_time(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) &
        Q(date__exact=date) &
        Q(period__exact=period) &
        Q(status__exact=1)
    )
    if koutei.count() == 0:
        return None
    else:
        ct = endy_max(line, date, period)
        if ct is None:
            return None
        else:
            return endj_max(line, date, period) + left_time(line, date, period)


# 「生産総数」を計算する関数
def all_cnt(line, date, period):
    dstr = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
    if line == '*':
        koutei = Process.objects.filter(
            Q(starty__gte=dstr + ' 0:00:00+09') &
            Q(starty__lte=dstr + ' 23:59:59+09') &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    else:
        koutei = Process.objects.filter(
            Q(line__exact=line) &
            Q(starty__gte=dstr + ' 0:00:00+09') &
            Q(starty__lte=dstr + ' 23:59:59+09') &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    if koutei.count() == 0:
        return 0
    else:
        cn = koutei.aggregate(Count('hinban'))
        return cn['hinban__count']


# 「生産完了」を計算する関数
def comp_cnt(line, date, period):
    dstr = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
    if line == '*':
        koutei = Process.objects.filter(
            Q(starty__gte=dstr + ' 0:00:00+09') &
            Q(starty__lte=dstr + ' 23:59:59+09') &
            Q(period__exact=period) &
            Q(endj__isnull=False) &
            Q(hinban__gt=0)
        )
    else:
        koutei = Process.objects.filter(
            Q(line__exact=line) &
            Q(starty__gte=dstr + ' 0:00:00+09') &
            Q(starty__lte=dstr + ' 23:59:59+09') &
            Q(period__exact=period) &
            Q(endj__isnull=False) &
            Q(hinban__gt=0)
        )
    if koutei.count() == 0:
        return 0
    else:
        cn = koutei.aggregate(Count('endj'))
        return cn['endj__count']


# 「生産進捗率」
def comp_prog(line, date, period):
    dstr = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
    if line == '*':
        koutei = Process.objects.filter(
            Q(starty__gte=dstr + ' 0:00:00+09') &
            Q(starty__lte=dstr + ' 23:59:59+09') &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    else:
        koutei = Process.objects.filter(
            Q(line__exact=line) &
            Q(starty__gte=dstr + ' 0:00:00+09') &
            Q(starty__lte=dstr + ' 23:59:59+09') &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    if koutei.count() == 0:
        return 0
    else:
        cm = koutei.aggregate(Count('endj'))
        cn = koutei.aggregate(Count('hinban'))
        if cm['endj__count'] is None or cm['endj__count'] == 0:
            return 0
        else:
            if cn['hinban__count'] is None or cn['hinban__count'] == 0:
                return 0
            else:
                return round(cm['endj__count'] / cn['hinban__count'] * 100, 1)


# 開始 or 終了
def start_or_end(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    # 開始の処理
    ql = Q(line__exact=koutei.line)
    qd = Q(date__exact=koutei.date)
    qp = Q(period__exact=koutei.period)
    if koutei.startj is None:
        nw = datetime.datetime.now().astimezone()
        # 切替時間を更新
        if koutei.value is not None:
            maxendj = Process.objects.all().filter(ql & qd & qp).aggregate(Max('endj'))
            if maxendj['endj__max'] is None:
                koutei.changej = 0
            else:
                dt = maxendj['endj__max'].astimezone()
                koutei.changej = get_stime(dt, nw)
        # 開始時間を更新
        koutei.startj = nw
        koutei.save()
    else:
        if koutei.endj is None:
            koutei.endj = datetime.datetime.now().astimezone()
            if koutei.name == '予備':
                koutei.processj = koutei.processy
            else:
                koutei.processj = get_stime(koutei.startj, koutei.endj)
        koutei.status = 1
        koutei.save()
    return redirect(request.META.get('HTTP_REFERER', '/', ))


# 所要時間計算
def get_stime(start_time, end_time):
    if start_time is None:
        return 0
    elif end_time is None:
        return 0
    else:
        td = end_time - start_time
        return round((td.days * 1440) + (td.seconds / 60))


# 生産中をキャンセル
def start_cancel(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    koutei.startj = None
    koutei.changej = None
    koutei.status = 0
    koutei.save()
    return redirect(request.META.get('HTTP_REFERER', '/', ))


# 編集
def edit(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    form = KouteiEditForm(request.POST, instance=koutei)
    template = 'edit2.html'
    # POST
    if request.method == 'POST':
        # バリデーションチェック
        if form.is_valid():
            koutei = form.save(commit=False)
            koutei.line = request.POST['line']
            koutei.date = request.POST['date']
            koutei.period = request.POST['period']
            if koutei.yosoku == '':
                koutei.yosoku = None
            # 数量に応じて生産数hを再計算
            if koutei.value is not None:
                if koutei.hdeki is not None and koutei.hdeki != 0:
                    koutei.processy = round(koutei.value / koutei.hdeki * 60)
            # 終了時間に応じて実際時間を計算しstatusを更新
            if koutei.endj is not None:
                if koutei.startj is not None:
                    if koutei.name == '予備':
                        koutei.processj = koutei.processy
                    else:
                        koutei.processj = get_stime(koutei.startj, koutei.endj)
                koutei.status = 1
            else:
                koutei.processj = None
                koutei.status = 0
            # 保存
            koutei.save()
            if 'next' in request.GET:
                return redirect(request.GET['next'])
        else:
            print("validation error: id=" + str(id))
    # GET
    else:
        form = KouteiEditForm(instance=koutei)
        template = 'edit2.html'
        if 'next' in request.GET:
            return redirect(request.GET['next'])
    return render(request, template, dict(form=form, id=id))


# 終了解除
def end_none(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    if request.method == 'POST':
        koutei.endj = None
        # 終了を解除、開始はそのまま
        koutei.processj = None
        koutei.status = 0
        koutei.save()
    return redirect('chourikoutei:list', koutei.line, koutei.date, koutei.period)


# plotly
def line_charts(date, period, line):
    if line is None:
        koutei = Process.objects.order_by('line').filter(
            Q(starty__gte=date + ' 0:00:00+09') &
            Q(starty__lte=date + ' 23:59:59+09') &
            Q(period__exact=period)
        )
        h = 800
    else:
        koutei = Process.objects.filter(
            Q(starty__gte=date + ' 0:00:00+09') &
            Q(starty__lte=date + ' 23:59:59+09') &
            Q(period__exact=period),
            Q(line__exact=line)
        )
        h = 240
    df = read_frame(koutei)

    # datetune列の内容をDatetime型かつaware(UTC)で、"*_utc"列に入れる
    df["start_utc"] = pd.to_datetime(df["starty"], utc=True)
    df["end_utc"] = pd.to_datetime(df["endy"], utc=True)
    # JSTに変換したデータを"*_jst"列に入れる
    df["start_jst"] = df["start_utc"].dt.tz_convert('Asia/Tokyo')
    df["end_jst"] = df["end_utc"].dt.tz_convert('Asia/Tokyo')
    # 製品名を簡略化する
    df["name_fix"] = df["name"].str.replace("ＬＷ", "")
    # ライン名をリンク化する
    df["line_fix"] = "<a href='/chouri/" + df["line"] + "/" + date + \
                     "/" + period + "/' target='_self'>" + df["line"] + "</a>"

    # 予備のstatusを1にする
    def func(x):
        if x["hinban"] < 100:
            return 1
        else:
            return x["status"]
    df["status_fix"] = df.apply(func, axis=1)

    fig = px.timeline(
        df, x_start="start_jst", x_end="end_jst", y="line_fix", text="name_fix",
        color="status_fix",
        color_continuous_scale=["aliceblue", "palegreen"],
        labels={'start_jst': '開始', 'end_jst': '終了', 'line_fix': '係',
                'name_fix': '仕掛品名', 'status_fix': '完了'},
        height=h,
    )
    fig.update_traces(
        width=0.95,
        textposition='inside',
        textfont=dict(color='black'),
    )
    fig.update_layout(
        uniformtext_mode=False,
        uniformtext_minsize=10,
        plot_bgcolor='blanchedalmond',
        clickmode='event+select',
    )
    fig.update_xaxes(
        title=dict(text='', font=dict(color='grey')),
        gridcolor='black', gridwidth=1,
    )
    fig.update_yaxes(
        title=dict(text='', font=dict(color='grey')),
        gridcolor='white', gridwidth=1,
        categoryorder='array',
        categoryarray=df['line_fix'][::-1],
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


class LineChartsView(TemplateView):
    model = Process
    context_object_name = 'kouteis'
    template_name = 'plot2.html'
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    form = MyModelForm(initial={'date': d, 'period': '昼勤'})

    def get_context_data(self, **kwargs):
        context = super(LineChartsView, self).get_context_data(**kwargs)
        dt = self.kwargs['date']
        pr = self.kwargs['period']
        context["plot"] = line_charts(dt, pr, None)
        # 製造日 ==========================================================================
        tdata = datetime.datetime.strptime(dt, '%Y-%m-%d')
        tdate = str(tdata.year) + '年' + str(tdata.month) + '月' + str(tdata.day) + '日'
        context['date'] = str(dt)
        context['datef'] = tdate
        context['periodf'] = pr
        return context

    def get_queryset(self, **kwargs):
        return Process.objects.order_by('line', 'starty').filter(
            Q(staty__gte=self.kwargs['date'] + ' 0:00:00+09') &
            Q(staty__lte=self.kwargs['date'] + ' 23:59:59+09') &
            Q(period__exact=self.kwargs['period']) &
            Q(hinban__gt=0)
        )

    @staticmethod
    def post(request):
        date = request.POST['date']
        period = request.POST['period']
        return render(request, 'chourikoutei:plot2', context={'date': date, 'period': period})


def download(request, **kwargs ):

    if request.method == 'POST':
        date = request.POST['date']
        period = request.POST['period']
    else:
        date = kwargs['date']
        period = kwargs['period']

    get_dekidaka()
    get_tounyu()

    return redirect('chourikoutei:list_all',date, period)


def get_dekidaka():

    tf = os.path.getmtime("data/dekidaka.csv")
    if Jisseki.objects.all().count() > 0:
        mx = Jisseki.objects.all().aggregate(Max('updated_at'))
        ts = mx['updated_at__max']
        if ts is None or ts == '':
            ts = 0
    else:
        ts = 0

    if tf > ts:
        Jisseki.objects.all().delete()
        df = pd.read_csv(
            'data/dekidaka.csv', skiprows=1, encoding='CP932',
            usecols=[0, 1, 2, 3, 4, 5, 6, 12, 13, 16, 21, 24, 31, 34],
            names=["date", "chain", "bin", "line", "hinban",
                   "name", "kubun", "shiji", "jisseki", "tantou",
                   "hinonflg", "kanetsu", "reikyaku", "kanryouflg"
                   ],
            dtype = {"date": object, "chain": str, "bin": int, "line": str, "hinban": int,
                     "name": str, "kubun": str, "shiji": float, "jisseki": float, "tantou": str,
                     "hinonflg": int, "kanetsu": str, "reikyaku": str,"kanryouflg": int
                     }
        )

        conn = psycopg2.connect(**connection_config)
        cur = conn.cursor()
        conn.set_isolation_level(0)
        tbl = 'chourikoutei_jisseki'
        col = ["date", "chain", "bin", "line", "hinban",
               "name", "kubun", "shiji", "jisseki", "tantou",
               "hinonflg", "kanetsu", "reikyaku", "kanryouflg"
               ]
        try:
            buf = StringIO()
            df.to_csv(buf, sep=',', na_rep='', index=False, header=False)
            buf.seek(0)
            cur.copy_from(buf, tbl, sep=',', null='', columns=col)
            conn.commit()
            cur.execute("UPDATE " + tbl + " SET updated_at = " + str(tf) + ";")

        except FileNotFoundError:
            print("失敗")

        finally:
            cur.close()
            conn.close()


def get_tounyu():

    tf = os.path.getmtime("data/tounyu.csv")
    if Tounyu.objects.all().count() > 0:
        mx = Tounyu.objects.all().aggregate(Max('updated_at'))
        ts = mx['updated_at__max']
        if ts is None or ts == '':
            ts = 0
    else:
        ts = 0

    if tf > ts:
        Tounyu.objects.all().delete()
        df = pd.read_csv(
            'data/tounyu.csv', skiprows=1, encoding='CP932',
            usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 17],
            names=["date", "chain", "bin", "line", "hinban", "name",
                   "kubun", "t_hinban", "t_name", "shiji", "jisseki",
                   "tantou", "kanryouflg"
                   ],
            dtype = {"date": object, "chain": str, "bin": int, "line": str, "hinban": int,
                     "name": str, "kubun": str, "t_hinban": int, "t_name": str,
                     "shiji": float, "jisseki": float, "tantou": str,"kanryouflg": int
                     }
        )

        conn = psycopg2.connect(**connection_config)
        cur = conn.cursor()
        conn.set_isolation_level(0)
        tbl = 'chourikoutei_tounyu'
        col = ["date", "chain", "bin", "line", "hinban", "name",
               "kubun", "t_hinban", "t_name", "shiji", "jisseki",
               "tantou", "kanryouflg"
               ]
        try:
            buf = StringIO()
            df.to_csv(buf, sep=',', na_rep='', index=False, header=False)
            buf.seek(0)
            cur.copy_from(buf, tbl, sep=',', null='', columns=col)
            conn.commit()
            cur.execute("UPDATE " + tbl + " SET updated_at = " + str(tf) + ";")

        except FileNotFoundError:
            print("失敗")

        finally:
            cur.close()
            conn.close()
