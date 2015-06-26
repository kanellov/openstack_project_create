import django.dispatch

project_created = django.dispatch.Signal(providing_args=["project", "user_id"])
