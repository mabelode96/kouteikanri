from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import Process
import bootstrap_datepicker_plus as datetimepicker


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
    date = DateChoiceField(
        queryset=Process.objects.all().distinct('date').order_by('-date'),
        label='製造日', to_field_name='date', empty_label='選択してください',
    )
    period = PeriodChoiceField(
        queryset=Process.objects.all().distinct('period').order_by('-period'),
        label='時間帯', to_field_name='period', empty_label='選択してください',
    )

    class Meta:
        model = Process
        fields = ('date', 'period')


class PeriodsChoiceForm(forms.Form):
    period = forms.fields.ChoiceField(
        choices = (('昼勤', '昼勤'), ('夜勤', '夜勤')),
        required=True, widget=forms.widgets.Select
    )


class KouteiEditForm(ModelForm):
    name = forms.CharField(
        label='品目名称', required=False, max_length=50,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    date = forms.DateField(label='製造日', required=False, widget=forms.HiddenInput())
    bin = forms.IntegerField(
        label='便', required=False, widget=forms.TextInput(attrs={'readonly': True})
    )
    hinban = forms.IntegerField(
        label='品目コード', required=False, widget=forms.HiddenInput()
    )
    yosoku = forms.CharField(
        label='予測生産', required=False, max_length=10,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    line = forms.CharField(
        label='係', required=False, max_length=50,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    period = forms.CharField(
        label='時間帯', required=False, max_length=50,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    value = forms.FloatField(label='指示量', required=False)
    unit = forms.IntegerField(label='単位', required=False)
    ctype = forms.IntegerField(label='調理種別', required=False)
    batdeki = forms.FloatField(label='バッチ当り出来高', required=False, widget=forms.HiddenInput())
    battime = forms.IntegerField(label='バッチ当り調理時間', required=False, disabled=False)
    hdeki = forms.FloatField(label='1時間当り出来高', required=False, widget=forms.HiddenInput())
    changey = forms.IntegerField(label='切替予定', required=False, widget=forms.NumberInput())
    processy = forms.IntegerField(label='作業予定', required=False, widget=forms.HiddenInput())
    starty = forms.DateTimeField(label='開始予定', required=False, disabled=False)
    endy = forms.DateTimeField(label='終了予定', required=False, disabled=False)
    shimej = forms.DateTimeField(label='締切時間', required=False)

    changej = forms.IntegerField(label='切替時間', required=False, widget=forms.NumberInput())
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
    processj = forms.IntegerField(label='作業時間', required=False, widget=forms.HiddenInput())
    status = forms.IntegerField(
        label='Status (0:開始前/生産中, 1:終了)', required=True,
        widget=forms.HiddenInput())

    class Meta:
        model = Process
        fields = ('id', 'hinban', 'name', 'bin', 'yosoku', 'line', 'period', 'date',
                  'value', 'unit', 'ctype', 'batdeki', 'battime', 'hdeki',
                  'changey', 'processy', 'starty', 'endy',
                  'shimej', 'changej', 'startj', 'endj', 'processj', 'status')
