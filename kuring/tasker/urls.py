from django.urls import path

from tasker.views import CreateTask, DetailTask, DeleteTask, TaskDashboard, UpdateTask

urlpatterns = [
    path('', TaskDashboard.as_view(), name='dashboard'),
    path('create/', CreateTask.as_view(), name='createTask'),
    path('detail/<int:pk>', DetailTask.as_view(), name='detailTask'),
    path('delete/<int:pk>', DeleteTask.as_view(), name='deleteTask'),
    path('update/<int:pk>', UpdateTask.as_view(), name='updateTask'),
]
