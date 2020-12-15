from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Process
from .forms import KouteiForm, KouteiEditForm, MyModelForm
from django.views.generic import ListView
from django.db.models import Q, Max, Min, Sum, Avg, Count
import datetime
from django.db import connection

# 検索
def top(request):
    f = MyModelForm()
    return render(request, 'kouteikanri/top.html', {'form1': f})


# 「総数」を計算する関数
def value_sum(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period)
    )
    if koutei.count() == 0:
        return 0
    else:
        return koutei.aggregate(Sum('value'))


# 「終了数」を計算する関数
def value_end(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period) &
        Q(status__exact=2)
    )
    if koutei.count() == 0:
        return 0
    else:
        return koutei.aggregate(Sum('value'))


# 「切替平均」を計算する関数
def change_avg(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period)
    )
    if koutei.count() == 0:
        return 0
    else:
        return koutei.aggregate(Avg('change'))


# 「終了予定」を取得する関数
def endy_max(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period)
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
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period)
    )
    if koutei.count() == 0:
        return None
    else:
        jm = koutei.aggregate(Max('end'))
        if jm['end__max'] is None:
            return None
        else:
            return jm['end__max'].astimezone()


# 「残り生産時間」を計算する関数
def left_time(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period) &
        Q(status__lt=2)
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


# 「終了予測」を計算する関数
def comp_time(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period) &
        Q(status__exact='2')
    )
    if koutei.count() == 0:
        return None
    else:
        ct = endy_max(line, date, period)
        if ct is None:
            return None
        else:
            return endj_max(line, date, period) + left_time(line, date, period)


def dict_fetchall(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# 全ライン
class AllList(ListView):
    model = Process
    context_object_name = 'result'
    template_name = 'kouteikanri/all.html'

#    def get_queryset(self, **kwargs):
#        # 製造日は当日固定
#        date = datetime.datetime.now().astimezone() - datetime.timedelta(hours=7)
#        dtStr = date.strftime("%Y-%m-%d")

#        koutei = Process.objects.filter(date__exact=dtStr, status__exact=2)
#        kouteis = koutei.values('line', 'period').annotate(
#            val_sum=Sum('value'),
#            proc_sum=Sum('processy'),
#        )

#        return kouteis

    def get_context_data(self, **kwargs):
        # 製造日は当日固定
        # date = datetime.datetime.now().astimezone() - datetime.timedelta(hours=7)
        # dtStr = date.strftime("%Y-%m-%d")
        dtStr = '2020-12-08'
        ctx = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor = connection.cursor()
            cursor.execute("SELECT line,period,"
                "Sum(value) AS val_sum,"
                "Sum(processy) AS proc_sum "
                "FROM kouteikanri_process "
                "WHERE date='"+dtStr+"' "
                "GROUP BY line,period;")
            tuple = cursor.fetchall()

        ctx['tuple'] = tuple
        ctx['date'] = dtStr
        return ctx

# 工程一覧
class KouteiList(ListView):
    model = Process
    context_object_name = 'kouteis'
    template_name = 'kouteikanri/list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ln = self.kwargs['line']
        dt = self.kwargs['date']
        pr = self.kwargs['period']
        ql = Q(line__exact=ln)
        qd = Q(date__exact=dt)
        qp = Q(period__exact=pr)
        # ライン名 ========================================================================
        ctx['linef'] = self.kwargs['line']
        # 製造日 ==========================================================================
        tstr = self.kwargs['date']
        tdata = datetime.datetime.strptime(tstr, '%Y-%m-%d')
        tdate = str(tdata.year)+'年'+str(tdata.month)+'月'+str(tdata.day)+'日'
        ctx['datef'] = tdate
        # 時間帯 ==========================================================================
        ctx['periodf'] = self.kwargs['period']
        # 終了予定 ========================================================================
        ctx['maxend'] = endy_max(ln, dt, pr)
        # 終了数/総数 ========================================================================
        ctx['valsum'] = value_sum(ln, dt, pr)
        ve = value_end(ln, dt, pr)
        ctx['valend'] = ve
        # 生産高 ===========================================================================
        sd = Process.objects.all().filter(ql & qd & qp).aggregate(Sum('seisand'))
        if sd['seisand__sum'] is None:
            sdstr = '0 円'
        else:
            sdstr = '{:,}'.format(round(sd['seisand__sum'] / 1000)) + ' 千円'
        ctx['sdstr'] = sdstr
        # 能率 =============================================================================
        stfavg = Process.objects.all().filter(
            ql & qd & qp & Q(status__exact='2')).aggregate(Avg('staff'))
        if stfavg['staff__avg'] is None:
            jin = 0
        else:
            jin = stfavg['staff__avg']
        sdEnd = Process.objects.all().filter(
            ql & qd & qp & Q(status__exact='2')).aggregate(Sum('seisand'))
        if sdEnd['seisand__sum'] is None:
            sdE = 0
        else:
            sdE = sdEnd['seisand__sum']
        minSt = Process.objects.all().filter(ql & qd & qp).aggregate(Min('start'))
        maxEn = Process.objects.all().filter(ql & qd & qp).aggregate(Max('end'))
        if minSt['start__min'] is None:
            tm = 0
        else:
            Smin = minSt['start__min']
            if maxEn['end__max'] is not None:
                Emax = maxEn['end__max']
                tm = get_stime(Smin, Emax) / 60
            else:
                tm = 0
        try:
            ctx['nouritsu'] = '{:,}'.format(round(sdE / tm / jin)) + ' 円'
        except ZeroDivisionError:
            ctx['nouritsu'] = '0 円'
        # 生産中の調査 ===================================================================
        cntst = Process.objects.all().filter(ql & qd & qp & Q(status__exact='1')).count()
        ctx['cntst'] = cntst
        # 切替平均 ======================================================================
        ctx['chavg'] = change_avg(ln, dt, pr)
        # 終了予測 ======================================================================
        ctx['comptime'] = comp_time(ln, dt, pr)
        # 進捗 ==========================================================================
        if endy_max(ln, dt, pr) is None:
            progress = 0
        else:
            progress = get_stime(comp_time(ln, dt, pr), endy_max(ln, dt, pr))
        ctx['progress'] = progress
        return ctx

    def get_queryset(self, **kwargs):
        return Process.objects.order_by('start', 'starty').filter(
            Q(line__exact=self.kwargs['line']) &
            Q(date__exact=self.kwargs['date']) &
            Q(period__exact=self.kwargs['period']))

    def post(self, request, **kwargs):
        print(request.POST)
        line = request.POST['line']
        date = request.POST['date']
        period = request.POST['period']
        return redirect('kouteikanri:list', line, date, period)


# 新規 or 編集
def edit(request, id=None):
    # 編集
    if id:
        koutei = get_object_or_404(Process, pk=id)
    # 新規
    else:
        koutei = Process()
    # POST
    if request.method == 'POST':
        form = KouteiEditForm(request.POST, instance=koutei)
        # バリデーションチェック
        if form.is_valid():
            koutei = form.save(commit=False)
            koutei.line = request.POST['line']
            koutei.period = request.POST['period']
            koutei.save()
            if 'next' in request.GET:
                return redirect(request.GET['next'])
    # GET
    else:
        form = KouteiEditForm(instance=koutei)
        if 'next' in request.GET:
            return redirect(request.GET['next'])
    return render(request, 'kouteikanri/edit.html', dict(form=form, id=id))


# 削除
def delete(request, id):
    koutei = get_object_or_404(Process, pk=id)
    koutei.delete()
    return redirect('kouteikanri:list', koutei.line, koutei.date, koutei.period)


# 開始 or 終了
def start_or_end(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    # 開始の処理
    ql = Q(line__exact=koutei.line)
    qd = Q(date__exact=koutei.date)
    qp = Q(period__exact=koutei.period)
    if koutei.start is None:
        nw = datetime.datetime.now().astimezone()
        # 切替時間を更新
        if koutei.value is not None:
            maxend = Process.objects.all().filter(ql & qd & qp).aggregate(Max('end'))
            if maxend['end__max'] is None:
                koutei.change = 0
            else:
                dt = maxend['end__max']
                koutei.change = get_stime(dt.astimezone(), nw)
        # 開始時間を更新
        koutei.start = nw
        koutei.status = 1
        koutei.save()
    # 終了の処理
    else:
        if koutei.end is None:
            koutei.end = datetime.datetime.now().astimezone()
            koutei.status = 2
            koutei.save()
    # 一覧のアンカーにジャンプ
    if Process.objects.all().filter(ql & qd & qp & Q(status__exact='2')).count() < 9:
        ancstr = None
    else:
        ancstr = str(koutei.id)
    return redirect('{}#'.format(reverse('kouteikanri:list',kwargs={
        'line': koutei.line,
        'date': koutei.date,
        'period': koutei.period
    })) + ancstr)


# 生産中をキャンセル
def start_cancel(request, **kwargs):
    # POST
    if request.method == 'POST':
        update_list = []
        line = request.POST['line']
        date = request.POST['date']
        dt = datetime.datetime.strptime(date, '%Y年%m月%d日')
        if dt is None:
            d = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            d = dt.strftime("%Y-%m-%d")
        period = request.POST['period']
        kouteis = Process.objects.all().filter(
            Q(line__exact=line) & Q(date__exact=d) &
            Q(period__exact=period) & Q(status__exact='1'))
        if kouteis.count() > 0:
            for koutei in kouteis:
                koutei.start = None
                koutei.status = 0
                update_list.append(koutei)
            # 生産中のデータを一括更新
            Process.objects.bulk_update(update_list, fields=["start", "status"])
        return redirect('kouteikanri:list', line, d, period)
        # 戻っても良い？
        # return redirect(request.META.get('HTTP_REFERER', '/'))


# 終了解除
def end_none(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    if request.method == 'POST':
        koutei.end = None
        # 生産中にする
        koutei.status = 1
        koutei.save()
    return redirect('kouteikanri:list', koutei.line, koutei.date, koutei.period)


# 所要時間計算
def get_stime(start_time, end_time):
    if start_time is None:
        return 0
    elif end_time is None:
        return 0
    else:
        td = end_time - start_time
        return round((td.days * 1440) + (td.seconds / 60))
