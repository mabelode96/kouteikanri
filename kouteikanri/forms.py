from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import process
import re


class KouteiForm(ModelForm):
    # モデルで定義された条件をオーバーライド？する（Metaの記述より先に書く）
    line = forms.CharField(required=False, max_length=50)
    date = forms.DateField(required=False)
    period = forms.CharField(required=False, max_length=10)
    name = forms.CharField(required=False, max_length=50)

    class Meta:
        model = process
        fields = ('id', 'line', 'date', 'period', 'bin',
                  'hinban', 'price', 'kubun', 'name',
                  'seisanh', 'value', 'seisand', 'conveyor',
                  'staff', 'panmm', 'slicev', 'slicep',
                  'changey', 'processy', 'starty', 'endy',
                  'start', 'end', 'change', 'status', 'kouteicd')

    # 各要素のバリデーション
#    def clean_email(self):
#        email = self.cleaned_data['email']
#        # 的にだがどりあえず
#        if re.match(r'.+@+', email) == None:
#            raise forms.ValidationError("メールアドレスではありません。")
#            return email


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

    class Meta:
        model = process
        fields = ('line', 'date', 'period',)

    line_fld = LineChoiceField(
        queryset=process.objects.all().distinct('line'),
        label='ライン名', to_field_name='line')
    date_fld = DateChoiceField(
        queryset=process.objects.all().distinct('date').order_by('-date'),
        label='製造日', to_field_name='date')
    period_fld = PeriodChoiceField(
        queryset=process.objects.all().distinct('period'),
        label='時間帯', to_field_name='period')
