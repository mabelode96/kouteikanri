import datetime

from django.db.models import Q, Count
from django.shortcuts import render
from django.views.generic import ListView

from kouteikanri.views import exec_query
from .forms import MyModelForm
from .models import Process


# 検索
def top(request):
    # 初期値を設定
    d = datetime.datetime.today().strftime("%Y-%m-%d")
    f = MyModelForm(initial={'date': d, 'period': '昼勤'})
    return render(request, 'top2.html', {'form1': f})


# 調理工程 全ライン一覧
def list_all(request):
    if request.method == 'POST':
        date = request.POST['date']
        period = request.POST['period']
        sql_text = (
                "SELECT line, period, "
                "count(hinban) AS all_cnt, "
                "count(endj) AS end_cnt, "
                "count(hinban) - count(endj) AS left_cnt, "
                "count(endj) * 100 / count(hinban) AS progress "
                "FROM kouteikanri_chouriproc "
                "WHERE date='" + date +
                "' AND period='" + period +
                "' AND hinban IS NOT NULL "
                "GROUP BY line, period "
                "ORDER BY period DESC, line;"
        )
        emp_list = exec_query(sql_text)
        return render(request, 'list_all.html', {
            'emp_list': emp_list, 'date': date, 'period': period})


# 調理工程
class List(ListView):
    model = Process
    context_object_name = 'kouteis'
    template_name = 'list2.html'
    paginate_by = 20
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
        return Process.objects.order_by('startj', 'starty').filter(
            Q(date__exact=self.kwargs['date']) &
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
    if line == '*':
        koutei = Process.objects.filter(
            Q(date__exact=date) &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    else:
        koutei = Process.objects.filter(
            Q(line__exact=line) &
            Q(date__exact=date) &
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
    if line == '*':
        koutei = Process.objects.filter(
            Q(date__exact=date) &
            Q(period__exact=period) &
            Q(endj__isnull=False) &
            Q(hinban__gt=0)
        )
    else:
        koutei = Process.objects.filter(
            Q(line__exact=line) &
            Q(date__exact=date) &
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
    if line == '*':
        koutei = Process.objects.filter(
            Q(date__exact=date) &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    else:
        koutei = Process.objects.filter(
            Q(line__exact=line) &
            Q(date__exact=date) &
            Q(period__exact=period) &
            Q(hinban__gt=0)
        )
    if koutei.count() == 0:
        return 0
    else:
        cm = koutei.aggregate(Count('endj'))
        cn = koutei.aggregate(Count('hinban'))
        if cm['endj__count'] is None:
            return 0
        else:
            if cn['hinban__count'] is None or cn['hinban__count'] == 0:
                return 0
            else:
                return round(cm['endj__count'] / cn['hinban__count'] * 100, 1)
