from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# custom CSV uploader.

from apps.zonprep_file_parsing.forms import ZonprepAppointmentCSVUploadForm



def home(request):
    if not request.user.is_authenticated:
        return render(request, "web/landing_page.html")
    zonprep_form = ZonprepAppointmentCSVUploadForm()
    return render(
        request,
        "web/app_home.html",
        context={
            "active_tab": "dashboard",
            "page_title": _("Dashboard"),
            "zonprep_form": zonprep_form,
        },
    )


def simulate_error(request):
    raise Exception("This is a simulated error.")
