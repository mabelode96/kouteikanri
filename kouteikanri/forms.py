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
        label='ライン名', to_field_name='line', empty_label='選択してください')
    date = DateChoiceField(
        queryset=Process.objects.all().distinct('date').order_by('-date'),
        label='製造日', to_field_name='date', empty_label='選択してください')
    period = PeriodChoiceField(
        queryset=Process.objects.all().distinct('period'),
        label='時間帯', to_field_name='period', empty_label='選択してください')

    class Meta:
        model = Process
        fields = ('line', 'date', 'period',)


class KouteiEditForm(ModelForm):
    name = forms.CharField(label='製品名', required=False, max_length=50,
                           widget = forms.TextInput(attrs={'readonly': True}))
    date = forms.DateField(label='製造日', required=False, widget=forms.HiddenInput())
    bin = forms.IntegerField(label='便', required=False,
                           widget = forms.TextInput(attrs={'readonly': True}))
    kubun = forms.CharField(label='区分', required=False, max_length=10,
                           widget = forms.TextInput(attrs={'readonly': True}))
    line = LineChoiceField(
        queryset=Process.objects.order_by('line').distinct('line'),
        label='ライン名', to_field_name='line', empty_label=None)
    period = PeriodChoiceField(
        queryset=Process.objects.order_by('period').distinct('period'),
        label='時間帯', to_field_name='period', empty_label=None)
    value = forms.IntegerField(label='数量', required=False)
    staff = forms.IntegerField(label='人員', required=False)
    startj = forms.DateTimeField(label='開始時間', required=False)
    endj = forms.DateTimeField(label='終了時間', required=False)
    changej = forms.IntegerField(label='切替時間', required=False)
    processj = forms.IntegerField(
        label='生産時間', required=False, widget=forms.HiddenInput())
    status = forms.IntegerField(
        label='Status (0:開始前/生産中, 1:終了)', required=True, widget=forms.HiddenInput())
    comment = forms.CharField(label='備考', required=False, max_length=255)

    class Meta:
        model = Process
        fields = ('id', 'name', 'bin', 'kubun',
                  'line', 'period', 'date', 'value', 'staff',
                  'startj', 'endj', 'changej', 'processj', 'comment', 'status')


class KouteiAddForm(ModelForm):
    line = forms.CharField(label='ライン名', required=True, widget=forms.HiddenInput())
    period = forms.CharField(label='時間帯', required=True, widget=forms.HiddenInput())
    date = forms.DateField(label='製造日', required=True, widget=forms.HiddenInput())
    name = forms.CharField(label='製品名', required=True, max_length=50,
                           widget = forms.TextInput(attrs={'readonly': False}))
    bin = forms.IntegerField(label='便', required=False,
                           widget = forms.TextInput(attrs={'readonly': False}))
    kubun = forms.CharField(label='区分', required=False, max_length=10,
                           widget = forms.TextInput(attrs={'readonly': False}))
    processy = forms.IntegerField(label='生産時間', required=True)
    status = forms.IntegerField(label='Status', required=True, widget=forms.HiddenInput())

    class Meta:
        model = Process
        fields = ('id', 'line', 'period', 'date', 'bin',
                  'hinban', 'price', 'kubun', 'name',
                  'seisanh', 'value', 'seisand', 'conveyor',
                  'staff', 'panmm', 'slicev', 'slicep',
                  'changey', 'processy', 'starty', 'endy', 'status')
