from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import process
import re


class LineModelForm(forms.ModelForm):
    queryset = process.objects.all().distinct('line')

    def __str__(self):
        return self.line

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
        queryset=process.objects.all().distinct('line'),
        label='ライン名', to_field_name='line', empty_label='ラインを選択してください')
    date = DateChoiceField(
        queryset=process.objects.all().distinct('date').order_by('-date'),
        label='製造日', to_field_name='date', empty_label='製造日を選択してください')
    period = PeriodChoiceField(
        queryset=process.objects.all().distinct('period'),
        label='時間帯', to_field_name='period', empty_label='時間帯を選択してください')

    class Meta:
        model = process
        fields = ('line', 'date', 'period',)


class KouteiForm(ModelForm):
    name = forms.CharField(label='製品名', required=False, max_length=50,
                           widget = forms.TextInput(attrs={'readonly':'readonly'}))
    date = forms.DateField(label='製造日', required=False, widget=forms.HiddenInput())
    bin = forms.IntegerField(label='便', required=False,
                           widget = forms.TextInput(attrs={'readonly':'readonly'}))
    kubun = forms.CharField(label='区分', required=False, max_length=10,
                           widget = forms.TextInput(attrs={'readonly':'readonly'}))
    # line = forms.CharField(label='ライン名', required=False, max_length=50)
    # period = forms.CharField(label='時間帯', required=False, max_length=10)
#    line_old = forms.CharField(required=True)
    line = LineChoiceField(
        queryset=process.objects.all().distinct('line'),
        label='ライン名', to_field_name='line', empty_label=None)
    period = PeriodChoiceField(
        queryset=process.objects.all().distinct('period'),
        label='時間帯', to_field_name='period', empty_label=None)
    hinban = forms.IntegerField(label='品番', required=False, widget=forms.HiddenInput())
    price = forms.FloatField(label='単価', required=False, widget=forms.HiddenInput())
    seisanh = forms.IntegerField(label='生産数h', required=False, widget=forms.HiddenInput())
    value = forms.IntegerField(label='数量', required=False)
    seisand = forms.FloatField(label='生産高', required=False, widget=forms.HiddenInput())
    conveyor = forms.FloatField(label='コンベア速度', required=False, widget=forms.HiddenInput())
    staff = forms.IntegerField(label='人員', required=False)
    panmm = forms.CharField(label='パンミリ数', required=False, max_length=50, widget=forms.HiddenInput())
    slicev = forms.IntegerField(label='スライス枚数', required=False, widget=forms.HiddenInput())
    slicep = forms.IntegerField(label='スライス能力', required=False, widget=forms.HiddenInput())
    changey = forms.IntegerField(label='切替予定', required=False, widget=forms.HiddenInput())
    processy = forms.IntegerField(label='生産時間', required=False, widget=forms.HiddenInput())
    starty = forms.DateTimeField(label='開始予定', required=False, widget=forms.HiddenInput())
    endy = forms.DateTimeField(label='終了予定', required=False, widget=forms.HiddenInput())
    start = forms.DateTimeField(label='開始時間', required=False)
    end = forms.DateTimeField(label='終了時間', required=False)
    change = forms.IntegerField(label='切替時間', required=False)
    status = forms.IntegerField(label='Status (0:開始前, 1:生産中, 2:終了)', required=True)
    kouteicd = forms.CharField(label='識別cd', required=False, max_length=100, widget=forms.HiddenInput())

    class Meta:
        model = process
        fields = ('id', 'name', 'bin', 'kubun',
                  'line', 'date', 'period','hinban', 'price',
                  'seisanh', 'value', 'seisand', 'conveyor',
                  'staff', 'panmm', 'slicev', 'slicep',
                  'changey', 'processy', 'starty', 'endy',
                  'start', 'end', 'change', 'status', 'kouteicd')

    # バリデーション
#    def clean_email(self):
#        email = self.cleaned_data['email']
#        if re.match(r'.+@+', email) == None:
#            raise forms.ValidationError("メールアドレスではありません。")
#            return email


