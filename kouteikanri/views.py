from django.shortcuts import render, get_object_or_404, redirect
from .models import Process
from .forms import KouteiEditForm, KouteiAddForm, MyModelForm
from django.views.generic import ListView
from django.db.models import Q, Max, Min, Sum, Avg, Count
import datetime
from django.db import connection


# blank
def blank(request):
    return render(request, 'kouteikanri/blank.html')


# 検索
def top(request):
    # 初期値を設定
    d = Process.objects.all().aggregate(Max('date'))
    f = MyModelForm(initial={'date': d['date__max']})
    return render(request, 'kouteikanri/top.html', {'form1': f})


# 全ライン一覧
# 参考url: https://qiita.com/t-iguchi/items/827865481e82bb32ad04
def all_list(request, **kwargs):
    if request.method == 'POST':
        date = request.POST['date']
        sql_text = (
                "SELECT line, period, "
                "sum(value) AS val_sum, "
                "sum(value * status) AS val_end_sum, "
                "sum(value) - sum(value * status) AS left_val, "
                "count(status) - sum(status) AS left_cnt, "
                "max(endy) AS endy_max, "
                "max(endj) AS endj_max, "
                "(sum(processy) + sum(changey)) - (sum(processy * status) + sum(changey * status)) AS left_time, "
                "(sum(processj * status) + sum(changej * status)) - (sum(processy * status) + sum(changey * status)) AS real_time, "
                "sum(value * status) * 100 / sum(value) AS progress "
                "FROM kouteikanri_process "
                "WHERE date='" + date + "' AND name <> '予備' "
                                        "GROUP BY line, period "
                                        "ORDER BY period DESC, line;"
        )
        emp_list = exec_query(sql_text)
        return render(request, 'kouteikanri/all.html', {'emp_list': emp_list, 'date': date})
#    else:
#        date = request.kwargs['date']
#        return redirect('kouteikanri:all', date)


# cursor.descriptionでフィールド名を配列にセットして、resultsにフィールド名を付加
def exec_query(sql_txt):
    with connection.cursor() as c:
        c.execute(sql_txt)
        results = c.fetchall()
        columns = []
        for field in c.description:
            columns.append(field.name)
        values = []
        for result in results:
            value_dic = {}
            for index, field in enumerate(columns):
                value_dic[field] = result[index]
            values.append(value_dic)
        return values


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
        qs = Q(status__exact=1)
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
        ctx['maxendy'] = endy_max(ln, dt, pr)
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
            ql & qd & qp & qs).aggregate(Avg('staff'))
        if stfavg['staff__avg'] is None:
            jin = 0
        else:
            jin = stfavg['staff__avg']
        sdEnd = Process.objects.all().filter(
            ql & qd & qp & qs).aggregate(Sum('seisand'))
        if sdEnd['seisand__sum'] is None:
            sdE = 0
        else:
            sdE = sdEnd['seisand__sum']
        minSt = Process.objects.all().filter(ql & qd & qp).aggregate(Min('startj'))
        maxEn = Process.objects.all().filter(ql & qd & qp).aggregate(Max('endj'))
        if minSt['startj__min'] is None:
            tm = 0
        else:
            Smin = minSt['startj__min']
            if maxEn['endj__max'] is not None:
                Emax = maxEn['endj__max']
                tm = get_stime(Smin, Emax) / 60
            else:
                tm = 0
        try:
            ctx['nouritsu'] = '{:,}'.format(round(sdE / tm / jin)) + ' 円'
        except ZeroDivisionError:
            ctx['nouritsu'] = '0 円'
        # 生産中の調査 ===================================================================
        cntst = Process.objects.all().filter(
            ql & qd & qp & Q(status__exact=0) & Q(startj__isnull=False)
        ).count()
        ctx['cntst'] = cntst
        # 切替平均 ======================================================================
        ctx['chavg'] = changej_avg(ln, dt, pr)
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
        return Process.objects.order_by('startj', 'starty').filter(
            Q(line__exact=self.kwargs['line']) &
            Q(date__exact=self.kwargs['date']) &
            Q(period__exact=self.kwargs['period']))

    def post(self, request, **kwargs):
        line = request.POST['line']
        date = request.POST['date']
        period = request.POST['period']
        return redirect('kouteikanri:list', line, date, period)


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
        Q(status__exact=1)
    )
    if koutei.count() == 0:
        return 0
    else:
        return koutei.aggregate(Sum('value'))


# 「切替平均」を計算する関数
def changej_avg(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period)
    )
    if koutei.count() == 0:
        return 0
    else:
        return koutei.aggregate(Avg('changej'))


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
        jm = koutei.aggregate(Max('endj'))
        if jm['endj__max'] is None:
            return None
        else:
            return jm['endj__max'].astimezone()


# 「残り生産時間」を計算する関数
def left_time(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period) &
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


# 「終了予測」を計算する関数
def comp_time(line, date, period):
    koutei = Process.objects.filter(
        Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period) &
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


# 新規 or 編集
def edit(request, id=None):
    # 編集
    if id:
        koutei = get_object_or_404(Process, pk=id)
        form = KouteiEditForm(request.POST, instance=koutei)
    # 新規
    else:
        koutei = Process()
        form = KouteiAddForm(request.POST, instance=koutei)
    # POST
    if request.method == 'POST':
        # バリデーションチェック
        if form.is_valid():
            koutei = form.save(commit=False)
            koutei.line = request.POST['line']
            koutei.date = request.POST['date']
            koutei.period = request.POST['period']
            if koutei.endj is not None:
                if koutei.startj is not None:
                    koutei.processj = get_stime(koutei.startj, koutei.endj)
                koutei.status = 1
            koutei.save()
            if 'next' in request.GET:
                return redirect(request.GET['next'])
    # GET
    else:
        if id:
            form = KouteiEditForm(instance=koutei)
        else:
            form = KouteiAddForm(instance=koutei)
        if 'next' in request.GET:
            return redirect(request.GET['next'])
    return render(request, 'kouteikanri/edit.html', dict(form=form, id=id))


# 終了解除
def end_none(request, id=id):
    koutei = get_object_or_404(Process, pk=id)
    if request.method == 'POST':
        koutei.endj = None
        # 終了を解除、開始はそのまま
        koutei.processj = None
        koutei.status = 0
        koutei.save()
    return redirect('kouteikanri:list', koutei.line, koutei.date, koutei.period)


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
    # 終了の処理
    else:
        if koutei.endj is None:
            koutei.endj = datetime.datetime.now().astimezone()
            koutei.processj = get_stime(koutei.startj, koutei.endj)
        koutei.status = 1
        koutei.save()
    return redirect('kouteikanri:list', koutei.line, koutei.date, koutei.period)


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
            Q(line__exact=line) & Q(date__exact=d) & Q(period__exact=period) &
            Q(status__exact=0) & Q(endj__isnull=True))
        if kouteis.count() > 0:
            for koutei in kouteis:
                koutei.startj = None
                koutei.changej = None
                koutei.status = 0
                update_list.append(koutei)
                ancstr = str(koutei.id)
            # 生産中のデータを一括更新
            Process.objects.bulk_update(
                update_list, fields=["changej", "startj", "status"])
        return redirect('kouteikanri:list', line, d, period)


# すべての実績をリセット
def reset_all(request, **kwargs):
    # POST
    if request.method == 'POST':
        update_list = []
        line = request.POST['line']
        date = request.POST['date']
        period = request.POST['period']
        kouteis = Process.objects.all().filter(
            Q(line__exact=line) & Q(date__exact=date) & Q(period__exact=period)
        )
        if kouteis.count() > 0:
            for koutei in kouteis:
                koutei.startj = None
                koutei.endj = None
                koutei.changej = None
                koutei.processj = None
                koutei.status = 0
                update_list.append(koutei)
            # 工程のデータを一括更新
            Process.objects.bulk_update(
                update_list, fields=["startj", "endj", "changej", "processj", "status"])
        return redirect('kouteikanri:list', line, date, period)
        # 戻ったほうが良い？
        # return redirect(request.META.get('HTTP_REFERER', '/'))


# 所要時間計算
def get_stime(start_time, end_time):
    if start_time is None:
        return 0
    elif end_time is None:
        return 0
    else:
        td = end_time - start_time
        return round((td.days * 1440) + (td.seconds / 60))
