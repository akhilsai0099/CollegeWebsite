from django import forms


class CourseApplicationForm(forms.Form):

    honors = forms.BooleanField(label="Honors", required=False)
    choice1 = forms.ChoiceField(
        label="Minors Choice 1")
    choice2 = forms.ChoiceField(
        label="Minors Choice 2", required=False)

    def __init__(self, values, *args, **kwargs):
        self.values = values
        super(CourseApplicationForm, self).__init__(*args, **kwargs)
        self.fields['choice1'].choices = self.values
        self.fields['choice1'].required = True
        self.fields['choice2'].choices = self.values
