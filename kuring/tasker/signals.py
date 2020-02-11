import django.dispatch

taskFinished = django.dispatch.Signal(providing_args=["taskId", "results"])
