from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import (
    AssessmentSession, SubjectLevel, Lesson,
    LessonProgress, StreakRecord, XPEvent,
    ChatSession, ChatMessage, UsageCounter
)
from university.models import TargetUniversity
from subscription.models import Subscription
from .ai_service import ai_service
from datetime import date, timedelta

class DashboardView(LoginRequiredMixin, View):
    template_name = 'study/dashboard.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        streak, _ = StreakRecord.objects.get_or_create(student=profile)
        today = date.today()
        if streak.last_active_date:
            if streak.last_active_date < today - timedelta(days=1):
                streak.current_streak = 1
                streak.save()

        xp_total = XPEvent.objects.filter(student=profile).aggregate(total=Sum('points'))['total'] or 0
        target_unis = TargetUniversity.objects.filter(student_profile=profile).select_related('university')
        subject_levels = SubjectLevel.objects.filter(student=profile)

        lessons = Lesson.objects.filter(student=profile)
        if not lessons.exists():
            default_subjects = ['Математика (SAT)', 'Английский (Reading & Writing)', 'Критическое мышление']
            for subj in default_subjects:
                content = ai_service.generate_lesson(subj, level='Intermediate', language=request.user.language)
                Lesson.objects.create(
                    student=profile,
                    subject=subj,
                    title=content['title'],
                    description=content['description'],
                    content=content,
                    language=request.user.language
                )
            lessons = Lesson.objects.filter(student=profile)

        completed_lesson_ids = LessonProgress.objects.filter(student=profile, status='completed').values_list('lesson_id', flat=True)
        counter, _ = UsageCounter.objects.get_or_create(user=request.user, date=today)
        has_pro = Subscription.objects.filter(user=request.user, status='active', ends_at__gte=timezone.now()).exists()

        context = {
            'profile': profile,
            'streak': streak,
            'xp_total': xp_total,
            'target_unis': target_unis,
            'subject_levels': subject_levels,
            'lessons': lessons,
            'completed_lesson_ids': set(completed_lesson_ids),
            'counter': counter,
            'has_pro': has_pro
        }
        return render(request, self.template_name, context)


class DiagnosticStartView(LoginRequiredMixin, View):
    template_name = 'study/diagnostic_start.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        target_count = TargetUniversity.objects.filter(student_profile=profile).count()
        return render(request, self.template_name, {'target_count': target_count, 'profile': profile})


class DiagnosticSessionView(LoginRequiredMixin, View):
    template_name = 'study/diagnostic_session.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        targets = [tu.university for tu in TargetUniversity.objects.filter(student_profile=profile).select_related('university')]
        if not targets:
            messages.warning(request, 'Пожалуйста, выберите хотя бы один целевой университет перед началом диагностики.')
            return redirect('university_list')

        session = AssessmentSession.objects.filter(student=profile, status='generated').first()
        if not session or not session.questions:
            questions = ai_service.generate_questions(targets, language=request.user.language, count=12)
            session = AssessmentSession.objects.create(
                student=profile,
                language=request.user.language,
                questions=questions,
                status='generated'
            )

        return render(request, self.template_name, {'session': session, 'questions': session.questions})

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        session_id = request.POST.get('session_id')
        session = get_object_or_404(AssessmentSession, id=session_id, student=profile)

        answers = {}
        for q in session.questions:
            qid = str(q['id'])
            val = request.POST.get(f'q_{qid}')
            if val is not None:
                answers[qid] = int(val)

        session.answers = answers
        evaluation = ai_service.evaluate_answers(session.questions, answers)
        session.status = 'evaluated'
        session.save()

        for subj, data in evaluation['subject_levels'].items():
            SubjectLevel.objects.update_or_create(
                student=profile,
                subject=subj,
                defaults={'level': data['level'], 'score': data['score']}
            )

        profile.onboarding_completed = True
        profile.save()

        XPEvent.objects.create(student=profile, points=100, reason='Завершение входной диагностики')
        streak, _ = StreakRecord.objects.get_or_create(student=profile)
        streak.last_active_date = date.today()
        streak.save()

        return redirect('diagnostic_result', session_id=session.id)


class DiagnosticResultView(LoginRequiredMixin, View):
    template_name = 'study/diagnostic_result.html'

    def get(self, request, session_id):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        session = get_object_or_404(AssessmentSession, id=session_id, student=profile)
        evaluation = ai_service.evaluate_answers(session.questions, session.answers)
        return render(request, self.template_name, {
            'session': session,
            'evaluation': evaluation,
            'profile': profile
        })


class LessonListView(LoginRequiredMixin, View):
    template_name = 'study/lesson_list.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        lessons = Lesson.objects.filter(student=profile)
        subject = request.GET.get('subject')
        if subject:
            lessons = lessons.filter(subject=subject)

        today = date.today()
        counter, _ = UsageCounter.objects.get_or_create(user=request.user, date=today)
        has_pro = Subscription.objects.filter(user=request.user, status='active', ends_at__gte=timezone.now()).exists()
        completed_ids = set(LessonProgress.objects.filter(student=profile, status='completed').values_list('lesson_id', flat=True))
        subjects = Lesson.objects.filter(student=profile).values_list('subject', flat=True).distinct()

        context = {
            'lessons': lessons,
            'subjects': subjects,
            'completed_ids': completed_ids,
            'counter': counter,
            'has_pro': has_pro
        }
        return render(request, self.template_name, context)


class LessonDetailView(LoginRequiredMixin, View):
    template_name = 'study/lesson_detail.html'

    def get(self, request, pk):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        lesson = get_object_or_404(Lesson, pk=pk, student=profile)
        progress, _ = LessonProgress.objects.get_or_create(lesson=lesson, student=profile)
        return render(request, self.template_name, {'lesson': lesson, 'progress': progress})

    def post(self, request, pk):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        lesson = get_object_or_404(Lesson, pk=pk, student=profile)
        progress, _ = LessonProgress.objects.get_or_create(lesson=lesson, student=profile)

        quiz = lesson.content.get('practice_quiz', [])
        correct_count = 0
        total = len(quiz)

        for idx, q in enumerate(quiz):
            val = request.POST.get(f'q_{idx}')
            if val is not None and int(val) == int(q['correct_index']):
                correct_count += 1

        score = (correct_count / total * 100) if total > 0 else 100

        if progress.status != 'completed':
            progress.status = 'completed'
            progress.score = score
            progress.completed_at = timezone.now()
            progress.save()

            XPEvent.objects.create(student=profile, points=lesson.xp_reward, reason=f'Урок: {lesson.title}')

            streak, _ = StreakRecord.objects.get_or_create(student=profile)
            today = date.today()
            if streak.last_active_date != today:
                if streak.last_active_date == today - timedelta(days=1):
                    streak.current_streak += 1
                else:
                    streak.current_streak = 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
                streak.last_active_date = today
                streak.save()

            messages.success(request, f'Отлично! Урок завершен. Получено +{lesson.xp_reward} XP!')
        else:
            messages.info(request, f'Вы повторили урок. Ваш результат: {score:.0f}%.')

        return redirect('lesson_detail', pk=lesson.id)


class GenerateLessonView(LoginRequiredMixin, View):
    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        has_pro = Subscription.objects.filter(user=request.user, status='active', ends_at__gte=timezone.now()).exists()
        if not has_pro:
            today = date.today()
            counter, _ = UsageCounter.objects.get_or_create(user=request.user, date=today)
            if counter.ai_lessons >= 3:
                messages.warning(request, 'Вы использовали дневной лимит бесплатных уроков (3/3). Оформите подписку Pro для неограниченной генерации!')
                return redirect('pricing')
            counter.ai_lessons += 1
            counter.save()

        subject = request.POST.get('subject', '').strip()
        if not subject:
            lowest = SubjectLevel.objects.filter(student=profile).order_by('score').first()
            subject = lowest.subject if lowest else 'Математика (SAT)'

        sl = SubjectLevel.objects.filter(student=profile, subject=subject).first()
        level = sl.level if sl else 'Intermediate'

        content = ai_service.generate_lesson(subject=subject, level=level, language=request.user.language)
        lesson = Lesson.objects.create(
            student=profile,
            subject=subject,
            title=content['title'],
            description=content['description'],
            content=content,
            language=request.user.language,
            status='ready',
            xp_reward=30
        )

        messages.success(request, f'Новый персональный урок "{lesson.title}" успешно сгенерирован ИИ!')
        return redirect('lesson_detail', pk=lesson.id)


class AIChatView(LoginRequiredMixin, View):
    template_name = 'study/chat.html'

    def get(self, request, session_id=None):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        sessions = ChatSession.objects.filter(student=profile)
        active_session = None
        if session_id:
            active_session = get_object_or_404(ChatSession, id=session_id, student=profile)
        elif sessions.exists():
            active_session = sessions.first()
        else:
            active_session = ChatSession.objects.create(student=profile, title='Консультация по поступлению')

        messages_list = active_session.messages.all() if active_session else []

        today = date.today()
        counter, _ = UsageCounter.objects.get_or_create(user=request.user, date=today)

        return render(request, self.template_name, {
            'sessions': sessions,
            'active_session': active_session,
            'messages_list': messages_list,
            'counter': counter
        })

    def post(self, request, session_id=None):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        active_session = get_object_or_404(ChatSession, id=session_id, student=profile)
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return redirect('chat_session', session_id=active_session.id)

        today = date.today()
        counter, _ = UsageCounter.objects.get_or_create(user=request.user, date=today)
        counter.ai_messages += 1
        counter.save()

        ChatMessage.objects.create(session=active_session, role='user', content=user_message)

        target_names = [tu.university.name for tu in TargetUniversity.objects.filter(student_profile=profile).select_related('university')]
        student_context = {
            'name': profile.full_name,
            'grade': profile.grade,
            'targets': ", ".join(target_names)
        }

        ai_response = ai_service.chat(
            history=[],
            user_message=user_message,
            student_context=student_context
        )

        ChatMessage.objects.create(session=active_session, role='assistant', content=ai_response)

        return redirect('chat_session', session_id=active_session.id)


class CreateChatSessionView(LoginRequiredMixin, View):
    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return redirect('profile_setup')

        title = request.POST.get('title', 'Новый диалог').strip() or 'Новый диалог'
        session = ChatSession.objects.create(student=profile, title=title)
        return redirect('chat_session', session_id=session.id)
