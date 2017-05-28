from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

from videoclases.models.pedagogical_questions.pedagogical_questions import PedagogicalQuestions


class PedagogicalQuestionsForm(ModelForm):

    class Meta:
         model = PedagogicalQuestions
         fields = '__all__'
         exclude= ['questions']
