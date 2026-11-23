from django import forms
from django.forms import ModelForm
from .models import TipPost, PostReport

class TipPostForm(ModelForm):
    class Meta:
        model = TipPost
        fields = ['university', 'title', 'body', 'language']
        widgets = {
            'university': forms.Select(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'placeholder': 'Как я поступил в Harvard: 5 ключевых советов'
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm',
                'rows': 8,
                'placeholder': 'Поделитесь подробными советами, структурой подготовки или инсайтами...'
            }),
            'language': forms.Select(choices=[('ru', 'Русский'), ('en', 'English'), ('tj', 'Тоҷикӣ')], attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3.5 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all shadow-sm'
            })
        }
        labels = {
            'university': 'Целевой университет (опционально)',
            'title': 'Заголовок совета',
            'body': 'Текст совета / статьи',
            'language': 'Язык'
        }


class PostReportForm(ModelForm):
    class Meta:
        model = PostReport
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'w-full bg-white border border-neutral-300 rounded-xl px-4 py-3 text-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-black shadow-sm',
                'rows': 4,
                'placeholder': 'Укажите причину жалобы...'
            })
        }
        labels = {
            'reason': 'Причина жалобы'
        }
