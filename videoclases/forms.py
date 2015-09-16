#-*- coding: UTF-8 -*-

from datetimewidget.widgets import DateWidget
from django import forms
from django.utils import timezone
from videoclases.models import *

class AsignarGrupoForm(forms.Form):
    grupos = forms.CharField(max_length=1000000000, required=True)
    tarea = forms.IntegerField(min_value=1, required=True)

class BorrarTareaForm(forms.Form):
    tarea = forms.IntegerField(min_value=1, required=True)

class ChangePasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': "Las contraseñas no coinciden.",
    }

    old_password = forms.CharField(label="Contraseña antigua",
                                   widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Nueva contraseña",
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirmar nueva contraseña",
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

class CrearCursoSubirArchivoForm(forms.Form):
    file = forms.FileField()
    nombre = forms.CharField(required=True)
    anho = forms.IntegerField(min_value=2015, required=True)

    def __init__(self, *args, **kwargs):
        super(CrearCursoSubirArchivoForm, self).__init__(*args, **kwargs)
        self.fields['anho'].label = "Año"
        self.fields['nombre'].label = "Nombre de curso"
        self.fields['file'].label = "Planilla"

class CrearTareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['video', 'titulo', 'descripcion', 'curso', 'revisiones', 
                  'fecha_subida', 'fecha_evaluacion']
        dateOptions = {
            'weekStart': 1,
            'todayHighlight': True,
            'startDate': timezone.now().strftime('%d-%m-%Y')
        }
        widgets = {
            'fecha_subida': DateWidget(options=dateOptions, usel10n=True),
            'fecha_evaluacion': DateWidget(options=dateOptions, usel10n=True),
        }

    def clean(self):
        fecha_subida = self.cleaned_data.get('fecha_subida')
        fecha_evaluacion = self.cleaned_data.get('fecha_evaluacion')
        if fecha_evaluacion < fecha_subida:
            msg = u'Fecha para evaluar debe ser posterior a Fecha para subir tarea.'
            self._errors['fecha_evaluacion'] = self.error_class([msg])

class EditarTareaForm(forms.ModelForm):

    class Meta:
        model = Tarea
        fields = ['video', 'titulo', 'descripcion', 'curso', 'revisiones', 
                  'fecha_subida', 'fecha_evaluacion']
        dateOptions = {
            'weekStart': 1,
            'todayHighlight': True,
            'startDate': timezone.now().strftime('%d-%m-%Y')
        }
        widgets = {
            'fecha_subida': DateWidget(options=dateOptions, usel10n=True),
            'fecha_evaluacion': DateWidget(options=dateOptions, usel10n=True),
        }

    def clean(self):
        if self.cleaned_data.get('fecha_subida'):
            fecha_subida = self.cleaned_data.get('fecha_subida')
        else:
            fecha_subida = self.instance.fecha_subida
        if self.cleaned_data.get('fecha_evaluacion'):
            fecha_evaluacion = self.cleaned_data.get('fecha_evaluacion')
        else:
            fecha_evaluacion = self.instance.fecha_evaluacion
        if fecha_evaluacion < fecha_subida:
            msg = u'Fecha para evaluar debe ser posterior a Fecha para subir tarea.'
            self._errors['fecha_evaluacion'] = self.error_class([msg])

    def __init__(self, *args, **kwargs):
        super(EditarTareaForm, self).__init__(*args, **kwargs)
        self.fields['video'].required = False
        self.fields['titulo'].required = False
        self.fields['descripcion'].required = False
        self.fields['curso'].required = False
        self.fields['revisiones'].required = False
        self.fields['fecha_subida'].required = False
        self.fields['fecha_evaluacion'].required = False

class EnviarVideoclaseForm(forms.ModelForm):

    class Meta:
        model = VideoClase
        fields = ['video', 'pregunta', 'alternativa_correcta', 
                  'alternativa_2', 'alternativa_3']

class EvaluacionesDeAlumnosForm(forms.ModelForm):

    class Meta:
        model = EvaluacionesDeAlumnos
        fields = ['valor', 'videoclase']

class RespuestasDeAlumnosForm(forms.ModelForm):

    class Meta:
        model = RespuestasDeAlumnos
        fields = ['videoclase', 'respuesta']

class SubirNotaForm(forms.Form):
    alumno = forms.IntegerField(min_value=1, required=True)
    grupo = forms.IntegerField(min_value=1, required=True)
    nota = forms.FloatField(min_value=1, max_value=7, required=True)