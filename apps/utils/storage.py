
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
# from django.core.files.storage import storages

class CustomGoogleCloudStorage(GoogleCloudStorage):
    def __init__(self, *args, **kwargs):
        # You can set specific settings for this storage
        kwargs['bucket_name'] = settings.GS_BUCKET_NAME
        # Initialize with the custom settings
        super().__init__(*args, **kwargs)
