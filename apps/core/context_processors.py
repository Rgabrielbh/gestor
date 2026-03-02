from django.conf import settings

def global_context(request):
    return {"APP_NAME": "NTT Data Gestão", "DEBUG": settings.DEBUG}
