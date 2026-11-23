from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import TipPost, AuthorTrust, PostReport
from .forms import TipPostForm, PostReportForm
from university.models import University

class PostListView(LoginRequiredMixin, View):
    template_name = 'community/post_list.html'

    def get(self, request):
        posts = TipPost.objects.filter(status='approved').select_related('author', 'university')
        query = request.GET.get('q', '').strip()
        university_id = request.GET.get('university', '').strip()

        if query:
            posts = posts.filter(title__icontains=query) | posts.filter(body__icontains=query)
        if university_id:
            posts = posts.filter(university_id=university_id)

        context = {
            'posts': posts,
            'universities': University.objects.filter(is_published=True),
            'selected_university': university_id,
            'query': query
        }
        return render(request, self.template_name, context)


class PostDetailView(LoginRequiredMixin, View):
    template_name = 'community/post_detail.html'

    def get(self, request, pk):
        post = get_object_or_404(TipPost, pk=pk)
        return render(request, self.template_name, {'post': post})


class PostCreateView(LoginRequiredMixin, View):
    template_name = 'community/post_create.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        is_admin_or_mod = request.user.role in ['admin', 'super_admin', 'moderator']
        is_verified = profile and profile.is_verified_student and profile.verified_university

        if not (is_verified or is_admin_or_mod):
            messages.warning(
                request,
                'Публиковать советы в сообществе могут только подтверждённые студенты университетов, прошедшие проверку.'
            )
            return redirect('student_verify')

        form = TipPostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        is_admin_or_mod = request.user.role in ['admin', 'super_admin', 'moderator']
        is_verified = profile and profile.is_verified_student and profile.verified_university

        if not (is_verified or is_admin_or_mod):
            messages.warning(
                request,
                'Публиковать советы в сообществе могут только подтверждённые студенты университетов, прошедшие проверку.'
            )
            return redirect('student_verify')

        form = TipPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if profile and profile.verified_university and not post.university:
                post.university = profile.verified_university

            trust, _ = AuthorTrust.objects.get_or_create(author=request.user)
            if trust.is_trusted or is_admin_or_mod:
                post.status = 'approved'
            else:
                post.status = 'approved'
                trust.approved_posts_count += 1
                if trust.approved_posts_count >= 3:
                    trust.is_trusted = True
                trust.save()

            post.save()
            messages.success(request, 'Ваш совет успешно опубликован в сообществе!')
            return redirect('post_detail', pk=post.id)

        return render(request, self.template_name, {'form': form})


class LikePostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(TipPost, pk=pk)
        post.likes_count += 1
        post.save()
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'post_list'
        return redirect(next_url)


class ReportPostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(TipPost, pk=pk)
        reason = request.POST.get('reason', '').strip()
        if reason:
            PostReport.objects.create(post=post, reporter=request.user, reason=reason)
            messages.success(request, 'Жалоба отправлена на рассмотрение модераторам.')
        return redirect('post_detail', pk=pk)
