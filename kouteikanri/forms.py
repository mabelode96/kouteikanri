import bootstrap_datepicker_plus as datetimepicker
from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import Process


class LineChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.line


class DateChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.date


class PeriodChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.period


class MyModelForm(forms.ModelForm):
    line = LineChoiceField(
        queryset=Process.objects.all().distinct('line'),
        label='ライン名', to_field_name='line', empty_label='選択してください'
    )
    date = DateChoiceField(
        queryset=Process.objects.all().distinct('date').order_by('-date'),
        label='製造日', to_field_name='date', empty_label='選択してください'
    )
    period = PeriodChoiceField(
        queryset=Process.objects.all().distinct('period').order_by('-period'),
        label='時間帯', to_field_name='period', empty_label='選択してください'
    )

    class Meta:
        model = Process
        fields = ('line', 'date', 'period',)


class KouteiEditForm(ModelForm):
    name = forms.CharField(
        label='製品名', required=False, max_length=50,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    date = forms.DateField(label='製造日', required=False, widget=forms.HiddenInput())
    bin = forms.IntegerField(
        label='便', required=False, widget=forms.TextInput(attrs={'readonly': True})
    )
    hinban = forms.IntegerField(
        label='品番', required=False, widget=forms.HiddenInput()
    )
    kubun = forms.CharField(
        label='区分', required=False, max_length=10,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    line = LineChoiceField(
        queryset=Process.objects.order_by('line').distinct('line'),
        label='ライン名', to_field_name='line', empty_label=None)
    period = PeriodChoiceField(
        queryset=Process.objects.order_by('period').distinct('period'),
        label='時間帯', to_field_name='period', empty_label=None)
    value = forms.IntegerField(label='数量', required=False)
    seisanh = forms.IntegerField(label='生産数/h', required=False)
    staff = forms.IntegerField(label='人員', required=False)
    slicev = forms.IntegerField(label='スライス枚数', required=False)
    startj = forms.DateTimeField(
        label='開始時間',
        required=False,
        disabled=False,
        widget=datetimepicker.DateTimePickerInput(
            format='%Y-%m-%d %H:%M:%S',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        )
    )
    endj = forms.DateTimeField(
        label='終了時間',
        required=False,
        disabled=False,
        widget=datetimepicker.DateTimePickerInput(
            format='%Y-%m-%d %H:%M:%S',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        )
    )
    changej = forms.IntegerField(
        label='切替時間',
        required=False,
        widget=forms.NumberInput()
    )
    processj = forms.IntegerField(
        label='生産時間', required=False, widget=forms.HiddenInput())
    status = forms.IntegerField(
        label='Status (0:開始前/生産中, 1:終了)', required=True,
        widget=forms.HiddenInput())
    comment = forms.CharField(
        label='備考', required=False, max_length=255, widget=forms.Textarea
    )

    class Meta:
        model = Process
        fields = ('id', 'hinban', 'name', 'bin', 'kubun', 'line',
                  'period', 'date', 'value', 'seisanh', 'staff', 'slicev',
                  'startj', 'endj', 'changej', 'processj', 'comment', 'status')


# 予備追加
class KouteiAddForm(ModelForm):
    line = forms.CharField(label='ライン名', required=True, widget=forms.HiddenInput())
    period = forms.CharField(label='時間帯', required=True, widget=forms.HiddenInput())
    date = forms.DateField(label='製造日', required=True, widget=forms.HiddenInput())
    bin = forms.IntegerField(label='便', required=False, widget=forms.HiddenInput())
    hinban = forms.IntegerField(label='品番', required=False, widget=forms.HiddenInput())
    price = forms.FloatField(label='単価', required=False, widget=forms.HiddenInput())
    name = forms.CharField(label='予備名称', required=True, max_length=50)
    kubun = forms.CharField(label='区分', required=False, max_length=10, widget=forms.HiddenInput())
    seisanh = forms.IntegerField(label='生産数h', required=False, widget=forms.HiddenInput())
    value = forms.IntegerField(label='数量', required=False, widget=forms.HiddenInput())
    seisand = forms.FloatField(label='生産高', required=False, widget=forms.HiddenInput())
    conveyor = forms.FloatField(label='コンベア速度', required=False, widget=forms.HiddenInput())
    staff = forms.IntegerField(label='人員', required=False, widget=forms.HiddenInput())
    panmm = forms.CharField(label='パンミリ数', required=False, max_length=50, widget=forms.HiddenInput())
    slicev = forms.IntegerField(label='スライス枚数', required=False, widget=forms.HiddenInput())
    slicep = forms.IntegerField(label='スライス能力', required=False, widget=forms.HiddenInput())
    changey = forms.IntegerField(label='切替予定', required=False, widget=forms.HiddenInput())
    processy = forms.IntegerField(label='生産時間', required=True)
    starty = forms.DateTimeField(
        label='開始時間',
        required=False,
        disabled=False,
        widget=datetimepicker.DateTimePickerInput(
            format='%Y-%m-%d %H:%M:%S',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        )
    )
    endy = forms.DateTimeField(
        label='終了時間',
        required=False,
        disabled=False,
        widget=datetimepicker.DateTimePickerInput(
            format='%Y-%m-%d %H:%M:%S',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        )
    )
    status = forms.IntegerField(label='Status', required=True, widget=forms.HiddenInput())

    class Meta:
        model = Process
        fields = ('id', 'line', 'period', 'date', 'bin',
                  'hinban', 'price', 'name', 'kubun',
                  'seisanh', 'value', 'seisand', 'conveyor',
                  'panmm', 'slicev', 'slicep', 'staff',
                  'changey', 'processy', 'starty', 'endy', 'status')


# 再生産（工程の複製）
class KouteiCopyForm(ModelForm):
    line = forms.CharField(label='ライン名', required=True, widget=forms.HiddenInput())
    period = forms.CharField(label='時間帯', required=True, widget=forms.HiddenInput())
    date = forms.DateField(label='製造日', required=True, widget=forms.HiddenInput())
    bin = forms.IntegerField(label='便', required=False, widget=forms.HiddenInput())
    hinban = forms.IntegerField(label='品番', required=False, widget=forms.HiddenInput())
    price = forms.FloatField(label='単価', required=False, widget=forms.HiddenInput())
    name = forms.CharField(
        label='製品名', required=True, max_length=50,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    kubun = forms.CharField(
        label='区分', required=False, max_length=10,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    seisanh = forms.IntegerField(label='生産数h', required=False, widget=forms.HiddenInput())
    value = forms.IntegerField(label='数量', required=False)
    seisand = forms.FloatField(label='生産高', required=False, widget=forms.HiddenInput())
    conveyor = forms.FloatField(label='コンベア速度', required=False, widget=forms.HiddenInput())
    staff = forms.IntegerField(label='人員', required=False)
    panmm = forms.CharField(label='パンミリ数', required=False, max_length=50, widget=forms.HiddenInput())
    slicev = forms.IntegerField(label='スライス枚数', required=False)
    slicep = forms.IntegerField(label='スライス能力', required=False, widget=forms.HiddenInput())
    changey = forms.IntegerField(label='切替予定', required=False)
    processy = forms.IntegerField(label='生産時間', required=True, widget=forms.HiddenInput())
    starty = forms.DateTimeField(
        label='開始時間',
        required=False,
        disabled=False,
        widget=datetimepicker.DateTimePickerInput(
            format='%Y-%m-%d %H:%M:%S',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        )
    )
    endy = forms.DateTimeField(
        label='終了時間',
        required=False,
        disabled=False,
        widget=datetimepicker.DateTimePickerInput(
            format='%Y-%m-%d %H:%M:%S',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
            }
        )
    )
    status = forms.IntegerField(label='Status', required=True, widget=forms.HiddenInput())

    class Meta:
        model = Process
        fields = ('id', 'line', 'period', 'date', 'bin',
                  'hinban', 'price', 'name', 'kubun',
                  'seisanh', 'value', 'seisand', 'conveyor',
                  'panmm', 'slicev', 'slicep', 'staff',
                  'changey', 'processy', 'starty', 'endy', 'status')


class KouteiCommentForm(forms.ModelForm):
    name = forms.CharField(
        label='製品名', required=True, max_length=50,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    comment = forms.CharField(
        label='備考', required=False, max_length=255,
        widget=forms.Textarea(attrs={'readonly': True})
    )

    class Meta:
        model = Process
        fields = ('id', 'name', 'comment',)
