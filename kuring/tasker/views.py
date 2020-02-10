from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from kuring.celery import app as celeryApp
from tasker import models, tasks


class TaskDashboard(ListView):
    """View to list the Task objects from the database"""
    model = models.Task
    template_name = 'dashboard.html'


class CreateTask(CreateView):
    """View to create the task"""
    model = models.Task
    fields = ['name']
    template_name = 'editTask.html'


class DeleteTask(DeleteView):
    """View to delete a task"""
    model = models.Task
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        """NOTE - This is necessary to avoid returning the "static deletion confirmation page."""
        return self.post(request, *args, **kwargs)


class DetailTask(DetailView):
    """View to provide details on the task"""
    model = models.Task
    template_name = 'detailTask.html'


class UpdateTask(UpdateView):
    """View to update the task"""
    model = models.Task
    fields = ['name']
    template_name = 'editTask.html'


class RunTask(DetailView):
    """View to launch a task"""
    model = models.Task
    template_name = 'detailTask.html'

    def get_object(self):

        obj = super().get_object()
        obj.status = models.Task.RUNNING
        obj.save()

        task_obj = tasks.add.delay(2, 3)
        obj.task_id = task_obj.id
        obj.save()

        return obj


class StopTask(DetailView):
    """View to stop a running task"""
    model = models.Task
    template_name = 'detailTask.html'

    def get_object(self):

        obj = super().get_object()

        celeryApp.control.revoke(obj.task_id, terminate=True)

        obj.status = models.Task.FINISHED
        obj.task_id = None
        obj.save()

        return obj
