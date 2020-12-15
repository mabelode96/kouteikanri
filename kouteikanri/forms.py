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
                           widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date = forms.DateField(label='製造日', required=False, widget=forms.HiddenInput())
    bin = forms.IntegerField(label='便', required=False,
                           widget = forms.TextInput(attrs={'readonly':'readonly'}))
    kubun = forms.CharField(label='区分', required=False, max_length=10,
                           widget = forms.TextInput(attrs={'readonly':'readonly'}))
    line = LineChoiceField(
        queryset=Process.objects.all().distinct('line'),
        label='ライン名', to_field_name='line', empty_label=None)
    period = PeriodChoiceField(
        queryset=Process.objects.all().distinct('period'),
        label='時間帯', to_field_name='period', empty_label=None)
    value = forms.IntegerField(label='数量', required=False)
    staff = forms.IntegerField(label='人員', required=False)
    start = forms.DateTimeField(label='開始時間', required=False)
    end = forms.DateTimeField(label='終了時間', required=False)
    change = forms.IntegerField(label='切替時間', required=False)
    status = forms.IntegerField(label='Status (0:開始前, 1:生産中, 2:終了)', required=True)

    class Meta:
        model = Process
        fields = ('id', 'name', 'bin', 'kubun',
                  'line', 'period', 'date', 'value', 'staff',
                  'start', 'end', 'change', 'status')
