from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import process
from .forms import KouteiForm, MyModelForm
from django.views.generic import ListView
from django.db.models import Q, Max, Min, Sum, Avg
import datetime


# 検索
def top(request):
    f = MyModelForm()
    return render(request, 'kouteikanri/top.html', {'form1': f})


# 工程一覧
class KouteiList(ListView):
    model = process
    context_object_name = 'kouteis'
    template_name = 'kouteikanri/list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ql = Q(line__exact=self.kwargs['line'])
        qd = Q(date__exact=self.kwargs['date'])
        qp = Q(period__exact=self.kwargs['period'])
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
        maxend = process.objects.all().filter(ql & qd & qp).aggregate(Max('endy'))
        if maxend['endy__max'] is None:
            ctx['maxend'] = None
        else:
            ctx['maxend'] = maxend['endy__max'].astimezone()
        # 終了/総数 ========================================================================
        valsum = process.objects.all().filter(ql & qd & qp).aggregate(Sum('value'))
        if valsum['value__sum'] is None:
            ctx['valsum'] = '0'
        else:
            ctx['valsum'] = valsum
        valend = process.objects.all().filter(
            ql & qd & qp & Q(status__exact='2')).aggregate(Sum('value'))
        if valend['value__sum'] is None:
            ctx['valend'] = '0'
        else:
            ctx['valend'] = process.objects.all().filter(
                ql & qd & qp & Q(status__exact='2')).aggregate(Sum('value'))
        # 生産高 ===========================================================================
        sd = process.objects.all().filter(ql & qd & qp).aggregate(Sum('seisand'))
        if sd['seisand__sum'] is None:
            sdstr = '0 円'
        else:
            sdstr = '{:,}'.format(round(sd['seisand__sum'] / 1000)) + ' 千円'
        ctx['sdstr'] = sdstr
        # 能率 =============================================================================
        stfavg = process.objects.all().filter(
            ql & qd & qp & Q(status__exact='2')).aggregate(Avg('staff'))
        if stfavg['staff__avg'] is None:
            jin = 0
        else:
            jin = stfavg['staff__avg']
        sdEnd = process.objects.all().filter(
            ql & qd & qp & Q(status__exact='2')).aggregate(Sum('seisand'))
        if sdEnd['seisand__sum'] is None:
            sdE = 0
        else:
            sdE = sdEnd['seisand__sum']
        minSt = process.objects.all().filter(ql & qd & qp).aggregate(Min('start'))
        maxEn = process.objects.all().filter(ql & qd & qp).aggregate(Max('end'))
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
        # 切替平均 ======================================================================
        cntst = process.objects.all().filter(
            ql & qd & qp & Q(status__exact='1')).count()
        ctx['cntst'] = cntst
        ctx['chavg'] = process.objects.all().filter(ql & qd & qp).aggregate(Avg('change'))
        # 終了予測 ======================================================================
        if process.objects.all().filter(ql & qd & qp & Q(status__exact='2')).count() == 0:
            if maxend['endy__max'] is None:
                comptime = None
            else:
                comptime = maxend['endy__max'].astimezone()
        else:
            sumPY = process.objects.all().filter(
                ql & qd & qp & Q(status__lt='2')).aggregate(Sum('processy'))
            if sumPY['processy__sum'] is None:
                py = 0
            else:
                py = sumPY['processy__sum']
            sumCY = process.objects.all().filter(
                ql & qd & qp & Q(status__lt='2')).aggregate(Sum('changey'))
            if sumCY['changey__sum'] is None:
                cy = 0
            else:
                cy = sumCY['changey__sum']
            tt = py + cy
            comptime = maxEn['end__max'].astimezone() + datetime.timedelta(minutes=tt)
        ctx['comptime'] = comptime
        # 進捗 ==========================================================================
        if maxend['endy__max'] is None:
            progress = 0
        else:
            progress = get_stime(comptime, maxend['endy__max'].astimezone())
        ctx['progress'] = progress
        return ctx

    def get_queryset(self, **kwargs):
        return process.objects.order_by('start', 'starty').filter(
            Q(line__exact=self.kwargs['line']) &
            Q(date__exact=self.kwargs['date']) &
            Q(period__exact=self.kwargs['period']))

    def post(self, request, **kwargs):
        line = request.POST['line']
        date = request.POST['date']
        period = request.POST['period']
        return redirect('kouteikanri:list', line, date, period)


# 新規 or 編集
def edit(request, id=None):
    # 編集
    if id:
        koutei = get_object_or_404(process, pk=id)
    # 新規
    else:
        koutei = process() # kouteiを追加
    # POST
    if request.method == 'POST':
        form = KouteiForm(request.POST, instance=koutei)
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
        form = KouteiForm(instance=koutei)
        if 'next' in request.GET:
            return redirect(request.GET['next'])
#        return render(request, 'kouteikanri/edit.html', dict(form=form, id=id, line_old=koutei.line))
    return render(request, 'kouteikanri/edit.html', dict(form=form, id=id))


# 削除
def delete(request, id):
    koutei = get_object_or_404(process, pk=id)
    koutei.delete()
    return redirect('kouteikanri:list', koutei.line, koutei.date, koutei.period)


# 開始 or 終了
def start_or_end(request, id=id, **kwargs):
    koutei = get_object_or_404(process, pk=id)
    # 開始の処理
    ql = Q(line__exact=koutei.line)
    qd = Q(date__exact=koutei.date)
    qp = Q(period__exact=koutei.period)
    if koutei.start is None:
        nw = datetime.datetime.now().astimezone()
#        nw = datetime.datetime.now(UTC)
        # 切替時間を更新
        if koutei.value is not None:
            maxend = process.objects.all().filter(ql & qd & qp).aggregate(Max('end'))
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
#            koutei.end = datetime.datetime.now(UTC)
            koutei.status = 2
            koutei.save()
    # 一覧のアンカーにジャンプ
    if process.objects.all().filter(ql & qd & qp & Q(status__exact='2')).count() < 9:
        ancstr = ''
    else:
        ancstr = str(koutei.id)
    return redirect('{}#'.format(reverse('kouteikanri:list',kwargs={
        'line': koutei.line,
        'date': koutei.date,
        'period': koutei.period
    })) + ancstr)


# 終了解除
def end_none(request, id=id):
    koutei = get_object_or_404(process, pk=id)
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
