from django.contrib import admin
from .models import Task, TaskSubmission, MonthlyRating

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'reward_coins', 'deadline', 'is_active', 'created_by',)
    list_filter = ('is_active',)

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status', 'created_at', 'reviewed_by',)
    list_filter = ('status',)
    actions = ['approve_submissions']

    def approve_submissions(self, request, queryset):
        for sub in queryset.filter(status='pending'):
            sub.approve(request.user)
        self.message_user(request, 'Выбранные задания одобрены и коины начислены.')
    approve_submissions.short_description = 'Одобрить выбранные задания.'

@admin.register(MonthlyRating)
class MothlyRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'completed_count')



# Register your models here.
