from django.contrib.auth import authenticate, login, logout,  get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
import random 
from django.contrib.sites.models import Site
from django.contrib.auth.views import PasswordResetView
from .utils import redirect_user_dashboard
import uuid

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')  # username OR email
        password = request.POST.get('password')

        user = None

        # Try email login
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            # Try username login
            user = authenticate(request, username=identifier, password=password)

        if user is None:
            messages.error(request, 'Invalid username/email or password.')
            return render(request, 'accounts/login.html')

        # Approval check
        if user.role in ['counsellor', 'peer'] and not user.is_approved:
            messages.error(request, 'Your account is awaiting admin approval.')
            return render(request, 'accounts/login.html')

        login(request, user)
        return redirect_user_dashboard(user)

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

User = get_user_model()


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            is_active=False
        )

        if role == 'student':
            user.is_approved = True
            user.save()

        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp}
        )

        send_mail(
            subject='Your Email Verification OTP',
            message=f'Your OTP is: {otp}\nValid for 10 minutes.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session['verify_user'] = user.id
        return redirect('verify_otp')

    return render(request, 'accounts/signup.html')



def verify_otp_view(request):
    user_id = request.session.get('verify_user')

    if not user_id:
        return redirect('signup')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        try:
            otp_obj = EmailOTP.objects.get(user=user)
        except EmailOTP.DoesNotExist:
            messages.error(request, 'OTP not found')
            return redirect('signup')

        if otp_obj.is_expired():
            messages.error(request, 'OTP expired')
            otp_obj.delete()
            return redirect('signup')

        if entered_otp == otp_obj.otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')
        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'accounts/verify_otp.html')

def logout_view(request):
    # Clear the specific session key
    if 'has_counted_login' in request.session:
        del request.session['has_counted_login']
    logout(request)
    return redirect('login')
class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    template_name = 'registration/password_reset_form.html'