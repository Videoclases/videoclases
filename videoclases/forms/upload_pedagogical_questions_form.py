from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML
from django import forms

from videoclases.models.course import Course
from videoclases.models.homework import Homework


class UploadPedagogicalQuestionsForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), label="Curso"
    )
    homework = forms.ModelChoiceField(
        queryset=Homework.objects.all(), label="Tarea"
    )
    file = forms.FileField()

    def clean_file(self):
        data = self.cleaned_data['file']
        if data._size > 2*1024*1024:
            raise forms.ValidationError("Archivo demasiado pesado")
        if not data.name.endswith(".xls"):
            raise forms.ValidationError("Solo se admite formato xls")
        return data

    def __init__(self, *args, **kwargs):
        super(UploadPedagogicalQuestionsForm, self).__init__(*args, **kwargs)

        helper = FormHelper(self)

        course = self.fields['course']
        course.widget.attrs['data-bind'] = "options: select.courses, optionsText: 'name', optionsValue: 'id', optionsCaption: '-- escoja un curso --', value: courses, valueAllowUnset: false"
        homework = self.fields['homework']
        homework.widget.attrs['data-bind'] = "options: homeworks, optionsText: 'name', optionsValue: 'id', value: homework, optionsCaption: '-- escoja una tarea --', valueAllowUnset: false"

        file = self.fields['file']
        file.widget.attrs['class'] = 'form-control'

        helper.form_class = 'form-horizontal '
        helper.form_method = 'post'
        helper.form_action = '.'

        helper.layout.append(
            FormActions(
                Submit('submit', u'Subir Archivo'),
                HTML("""<a
                        href=""
                        class="btn btn-default">Descargar Plantilla</a>""")
            )
        )
        self.helper = helper
