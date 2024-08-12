from django import forms

class ZonprepAppointmentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV file',
        widget=forms.FileInput(attrs={'accept': '.csv'}),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('This file is not a CSV file.')

        if csv_file.content_type != 'text/csv':
            raise forms.ValidationError('This file is not of type text/csv.')

        return csv_file
