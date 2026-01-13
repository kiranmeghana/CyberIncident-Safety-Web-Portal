from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
import random 
from django.contrib.auth.views import PasswordResetView
from .utils import redirect_user_dashboard

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')

        user = None
        try:
            # Handle Email or Username login
            if '@' in identifier:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = authenticate(request, username=identifier, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            # CRITICAL CHECK: Regular users are is_active=False until OTP verify
            if not user.is_active:
                messages.error(request, 'Please verify your email/OTP before logging in.')
                return render(request, 'accounts/login.html')

            # Admin Approval Check
            if user.role == 'admin' and not user.is_approved:
                messages.error(request, 'Admin account pending approval.')
                return render(request, 'accounts/login.html')
            
            # Successful Login
            login(request, user)
            user.login_count += 1
            user.save()

            # ROLE REDIRECT
            if user.is_superuser or user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                # Use the NAMED URL from i18n_patterns in core/urls.py
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
            
    return render(request, 'accounts/login.html')
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'student')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')

        user = User.objects.create_user(
            username=username, email=email, password=password, 
            role=role, is_active=False
        )

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        try:
            send_mail(
                'Verify Your Cyber Portal Account',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['verify_user'] = user.id
            return redirect('verify_otp')
        except Exception:
            messages.error(request, 'Error sending email. Please try again.')

    return render(request, 'accounts/signup.html')

def verify_otp_view(request):
    user_id = request.session.get('verify_user')
    if not user_id: return redirect('signup')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).first()

        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')
        else:
            messages.error(request, 'Invalid or expired OTP.')

    return render(request, 'accounts/verify_otp.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'