from django import forms
from .models import Notice, Assignment, Timetable, FAQ


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notice title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notice description',
                'rows': 5
            }),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'subject', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assignment title'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Assignment description',
                'rows': 5
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['day', 'subject', 'start_time', 'end_time']
        widgets = {
            'day': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monday'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Frequently asked question'
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Answer',
                'rows': 5
            }),
        }