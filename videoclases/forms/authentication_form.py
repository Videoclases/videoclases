from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from django.contrib.auth.forms import AuthenticationForm


class CustomAutheticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAutheticationForm, self).__init__(*args, **kwargs)

        helper = FormHelper(self)
        helper.form_class = 'form-inline'
        helper.form_method = 'post'
        helper.form_action = '.'
        helper.field_class ='form-group'
        helper.form_show_labels = False
        helper.layout.insert(2, HTML(u'<button type="submit" class="btn btn-info btn-sm"><span class="glyphicon glyphicon-user"></span> Ingresar</button>'))

        self.helper = helper
