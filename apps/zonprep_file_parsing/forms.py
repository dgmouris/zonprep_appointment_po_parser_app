from django import forms

class ZonprepAppointmentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV file',
        widget=forms.FileInput(attrs={'accept': '.csv'}),
    )
    send_to_external_fullfillment = forms.BooleanField(
        label='Send to External Fullfillment',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('This file is not a CSV file.')

        if csv_file.content_type != 'text/csv':
            raise forms.ValidationError('This file is not of type text/csv.')

        return csv_file


