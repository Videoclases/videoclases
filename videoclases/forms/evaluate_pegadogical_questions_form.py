# coding=utf-8
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm
from django import forms


class EvaluatePedagogicalQuestionsForm(forms.Form):

    def __init__(self, student, pegadogical_questions,*args, **kwargs):
        super(EvaluatePedagogicalQuestionsForm, self).__init__(*args, **kwargs)
        for question in pegadogical_questions.questions.all():
            self.fields[u"{0}".format(question.id)] = forms.ModelChoiceField(queryset=question.alternatives.all(),label= u"{0}".format(question))

        helper = FormHelper(self)

        helper.form_class = 'form-horizontal '
        helper.form_method = 'post'
        helper.form_action = '.'

        helper.layout.append(
            FormActions(
                Submit('submit', u'Enviar Test'),
            )
        )
        self.helper = helper
