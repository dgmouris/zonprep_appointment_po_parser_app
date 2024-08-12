from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# custom CSV uploader.

from apps.zonprep_file_parsing.forms import ZonprepAppointmentCSVUploadForm
from apps.zonprep_file_parsing.csv_processor import process_csv


def home(request):
    if not request.user.is_authenticated:
        return render(request, "web/landing_page.html")
    submitted = False
    created_appointments = 0
    already_created_appointments = 0
    if request.method == 'POST':
        zonprep_form = ZonprepAppointmentCSVUploadForm(request.POST, request.FILES)
        if zonprep_form.is_valid():
            # Process the form data
            csv_file = zonprep_form.cleaned_data['csv_file']
            # process the csv file
            results = process_csv(csv_file)
            created_appointments = results['created_appointments']
            already_created_appointments = results['already_created_appointments']
            submitted = True
    else:
        zonprep_form = ZonprepAppointmentCSVUploadForm()

    return render(
        request,
        "web/app_home.html",
        context={
            "active_tab": "dashboard",
            "page_title": _("Dashboard"),
            "zonprep_form": zonprep_form,
            "submitted": submitted,
            "created_appointments": created_appointments,
            "already_created_appointments": already_created_appointments,
        },
    )


def simulate_error(request):
    raise Exception("This is a simulated error.")
