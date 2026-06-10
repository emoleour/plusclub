from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
#from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Task, TaskSubmission, MonthlyRating
from .forms import TaskForm
from apps.users.views import is_admin
from apps.notifications.utils import create_notification


@login_required
def task_list(request):
    """Список активных заданий для пользователя"""
    tasks = Task.objects.filter(is_active=True, deadline__gt=timezone.now())

    user_submissions = {sub.task_id: sub for sub in request.user.submissions.all()}
    context = {
        'tasks': tasks,
        'user_submissions': user_submissions,
    }
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail(request, task_id):
    """Страница выполнения задания"""
    task = get_object_or_404(Task, id=task_id, is_active=True)

    if TaskSubmission.objects.filter(task=task, user=request.user).exists():
        messages.warning(request, 'Вы уже отправили отклик на это задание.')
        return redirect('task_list')
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        comment = request.POST.get('comment', '')
        if not photo:
            messages.error(request, 'Необходимо загрузить фото.')
            return render(request, 'tasks/task_detail.html', {'task': task})
        TaskSubmission.objects.create(
            task=task,
            user=request.user,
            photo=photo,
            comment=comment
        )
        messages.success(request, 'Задание отправлено на проверку.')
        return redirect('task_list')
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def submission_history(request):
    """История откликов текущего пользователя"""
    submissions = request.user.submissions.order_by('-created_at')
    return render(request, 'tasks/submission_history.html', {'submissions': submissions})

@login_required
@user_passes_test(is_admin)
def review_list(request):
    """Список всех откликов для проверки админом"""

    status_filter = request.GET.get('status', '')
    submissions = TaskSubmission.objects.select_related('task', 'user').order_by('created_at')
    if status_filter in ('pending', 'approved', 'rejected'):
        submissions = submissions.filter(status=status_filter)

    #пагинация по 20 откликов на странице
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'tasks/review_list.html', context)

@login_required
@user_passes_test(is_admin)
def review_detail(request, submission_id):
    """Детальный просмотр одного отклика и выполнение действий"""
    submission = get_object_or_404(TaskSubmission.objects.select_related('task', 'user'), id=submission_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve' and submission.status == 'pending':
            submission.approve(request.user)
            create_notification(
                user=submission.user,
                title='Задание одобрено',
                message=f'Ваше задание"{submission.task.title}" одобрено. Начислено {submission.task.reward_coins} коинов.',
                link='/tasks/history'
            )
            messages.success(request, f'Отклик пользователя {submission.user.email} одобрен. Начислено {submission.task.reward_coins} коинов.')
        elif action == 'reject' and submission.status == 'pending':
            submission.status == 'rejected'
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.save()
            messages.warning(request, 'Отклик отклонён.')
        return redirect('review_list')
    context = {'submission': submission}
    return render(request, 'tasks/review_detail.html', context)


@login_required
def mothly_rating(request):
    """рейтинг пользователей за текущий месяц"""
    now = timezone.now()

    ratings = MonthlyRating.objects.filter(year=now.year, month=now.month).order_by('-completed_count')[:20]
    return render(request, 'tasks/rating.html', {'ratings': ratings, 'month': now.month, 'year': now.year})

@login_required
@user_passes_test(is_admin)
def task_manage_list(request):
    """Список всех заданий"""
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'tasks/task_manage_list.html', {'tasks': tasks})

@login_required
@user_passes_test(is_admin)
def task_manage_create(request):
    """Создание нового задания"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            messages.success(request, 'Задание создано.')
            return redirect('task_manage_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_manage_form.html', {'form': form, 'action': 'create'})

@login_required
@user_passes_test(is_admin)
def task_manage_update(request, task_id):
    """Редактирование задания"""

    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задание обновлено.')
            return redirect('task_manage_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_manage_form.html', {'form': form, 'action': 'update', 'task': task})

@login_required
@user_passes_test(is_admin)
def task_manage_delete(request, task_id):
    """Удаление задания"""

    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задание удалено.')
        return redirect('task_manage_list')
    return render(request, 'tasks/task_manage_confirm_delete.html', {'task': task})


# Create your views here.
