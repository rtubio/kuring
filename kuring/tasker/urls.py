from django.urls import path

from tasker.views import CreateTask, DetailTask, DeleteTask, RunTask, StopTask, TaskDashboard, UpdateTask

urlpatterns = [
    path('', TaskDashboard.as_view(), name='dashboard'),
    path('create/', CreateTask.as_view(), name='createTask'),
    path('detail/<int:pk>', DetailTask.as_view(), name='detailTask'),
    path('delete/<int:pk>', DeleteTask.as_view(), name='deleteTask'),
    path('update/<int:pk>', UpdateTask.as_view(), name='updateTask'),
    path('run/<int:pk>', RunTask.as_view(), name='runTask'),
    path('stop/<int:pk>', StopTask.as_view(), name='stopTask'),
]
