import datetime
from django.db.models import Q, Count
from django.shortcuts import render
from django.views.generic import ListView
from .forms import MyModelForm
from .models import Process
import plotly.express as px
import pandas as pd
from django.views.generic import TemplateView
from django_pandas.io import read_frame


# 検索
def top(request):
    # 初期値を設定
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    f = MyModelForm(initial={'date': d, 'period': '昼勤'})
    return render(request, 'top2.html', {'form1': f})


# リダイレクト用
def redirect_b(request):
    if request.method == 'POST':
        date = request.POST['date']
        period = request.POST['period']
        return render(request, 'redirect2.html', {'date': date, 'period': period})


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
        return Process.objects.filter(starty__gte=s, starty__lte=e, period__exact=p) \
            .values("line", "period") \
            .annotate(all_cnt=Count("hinban"),
                      end_cnt=Count("endj"),
                      left_cnt=Count("hinban") - Count("endj"),
                      progress=Count("endj") * 100 / Count("hinban")
                      )

    @staticmethod
    def post(request):
        date = request.POST['date']
        period = request.POST['period']
        return render(request, 'chourikoutei:list_all', context={'date': date, 'period': period})


# 調理工程
class List(ListView):
    model = Process
    context_object_name = 'kouteis'
    template_name = 'list2.html'
    paginate_by = 15
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    form = MyModelForm(initial={'date': d, 'period': '昼勤'})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 製造日 ==========================================================================
        tstr = self.kwargs['date']
        tdata = datetime.datetime.strptime(tstr, '%Y-%m-%d')
        tdate = str(tdata.year) + '年' + str(tdata.month) + '月' + str(tdata.day) + '日'
        ctx['datef'] = tdate
        # 時間帯 ==========================================================================
        ctx['periodf'] = self.kwargs['period']
        ctx['linef'] = self.kwargs['line']
        # セット総数 =======================================================================
        ctx['all_cnt'] = all_cnt(ctx['linef'], tdata, ctx['periodf'])
        # セット総数 =======================================================================
        ctx['comp_cnt'] = comp_cnt(ctx['linef'], tdata, ctx['periodf'])
        # 進捗 ============================================================================
        ctx['progress'] = comp_prog(ctx['linef'], tdata, ctx['periodf'])
        return ctx

    def get_queryset(self, **kwargs):
        return Process.objects.order_by('endj', 'starty').filter(
            Q(starty__gte=self.kwargs['date'] + ' 0:00:00+09') &
            Q(starty__lte=self.kwargs['date'] + ' 23:59:59+09') &
            Q(period__exact=self.kwargs['period']) &
            Q(line__exact=self.kwargs['line']) &
            Q(hinban__gt=0))

    @staticmethod
    def post(request):
        date = request.POST['date']
        period = request.POST['period']
        line = request.POST['line']
        return render(request, 'chourikoutei:list',
                      context={'date': date, 'period': period, 'line': line})


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


# plotly
def line_charts(date, period):
    koutei = Process.objects.order_by('line').filter(
        Q(starty__gte=date + ' 0:00:00+09') &
        Q(starty__lte=date + ' 23:59:59+09') &
        Q(period__exact=period)
    )
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
                'name_fix': '仕掛品名', 'status_fix': '状態'},
        #height=900,
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
        context["plot"] = line_charts(dt, pr)
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
