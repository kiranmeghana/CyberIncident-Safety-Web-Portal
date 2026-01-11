import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import user_passes_test  , login_required
from .models import Incident
from .utils import analyze_cyber_risk
import google.generativeai as genai
import base64
from django.contrib.auth import get_user_model



genai.configure(api_key=settings.AI_API_KEY)



# Use BLOCK_NONE to ensure technical cyber terms aren't flagged as "Harassment" or "Hate Speech"
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# --- Authentication Views ---

def signup_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        passw = request.POST.get('password')
        
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')
            
        user = User.objects.create_user(uname, email, passw)
        user.is_active = False  # Account remains inactive until email verification
        user.save()
        
        # Email Verification Logic
        subject = "Verify Your Defence Portal Account"
        # In production, replace 127.0.0.1 with your actual domain
        verify_url = f"http://127.0.0.1:8000/verify/{uname}/"
        message = f"Hi {uname}, please use this link to verify your account: {verify_url}"
        
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Registration successful! Please check your email to verify.")
        except Exception:
            messages.warning(request, "Account created, but email failed to send. Please contact admin.")
            
        return redirect('login')
        
    return render(request, 'auth/signup.html')

def login_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        passw = request.POST.get('password')
        user = authenticate(request, username=uname, password=passw)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Please verify your email first.")
        else:
            messages.error(request, "Invalid credentials.")
            
    return render(request, 'auth/login.html')

def verify_email(request, username):
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        messages.success(request, "Account verified! You can now login.")
        return redirect('login')
    except User.DoesNotExist:
        return HttpResponse("Invalid verification link.", status=404)


# --- Core Functional Views ---

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard') # Now this name exists in urls.py
    return render(request, 'landing.html')
    
    # Ensure this file exists at templates/portal/landing.html
    return render(request, 'portal/landing.html')

# Update your report_incident view and add the extraction helper below it
def report_incident(request):
    is_anon_param = request.GET.get('anonymous') == 'true'
    
    if request.method == 'POST':
        itype = request.POST.get('incident_type')
        desc = request.POST.get('description')
        evid = request.FILES.get('evidence')

        # 1. API-DRIVEN RECOMMENDATIONS (Multiple Points)
        model = genai.GenerativeModel("gemini-2.5-flash")
        recommendation_prompt = (
        f"Role: CSOC Commander (Indian Defence). Input Category: {itype}. Incident: {desc}. "
        "Task: Generate a detailed JSON object with 'dos' and 'donts'. "
        "CRITICAL: Break down complex instructions into multiple simple points. "
        "Each point must be a single, clear action (max 15 words). "
        "Mandatory: Return exactly 6 technical SOPs for each list. "
        "Format: Return ONLY valid JSON."
        )
        try:
            raw_ai = model.generate_content(recommendation_prompt).text
            # Clean JSON and parse
            guidance = json.loads(raw_ai.replace('```json', '').replace('```', '').strip())
        except:
            # High-detail fallback
            guidance = {
                'dos': ['Isolate the terminal from the unit VLAN', 'Execute volatile memory dump', 'Preserve all system event logs', 'Revoke MFA tokens across all defence portals', 'Notify the Unit Security Officer (USO)', 'Submit a formal report to CERT-In'],
                'donts': ['Do not reboot the system (preserves evidence)', 'Do not communicate via unencrypted mobile nets', 'Do not run unauthorized antivirus scans', 'Do not delete any temporary browser cache', 'Do not attempt manual file recovery', 'Do not pay any ransom or engage with threat actors']
            }

        score, level, advice = analyze_cyber_risk(desc)

        incident = Incident.objects.create(
            user=request.user if request.user.is_authenticated else None,
            incident_type=itype, description=desc, evidence=evid,
            risk_score=score, risk_level=level,
            is_anonymous=is_anon_param or (request.POST.get('is_anonymous') == 'on')
        )

        return render(request, 'portal/recommendations.html', {
            'incident': incident,
            'dos': guidance['dos'],
            'donts': guidance['donts']
        })
        
    return render(request, 'portal/report_form.html', {'is_anon': is_anon_param})

# ADD THIS NEW VIEW for the AJAX API Call
# def api_extract_image(request):
#     if request.method == 'POST' and request.FILES.get('image')
#         image_file = request.FILES['image']
#         model = genai.GenerativeModel("gemini-2.5-flash")
#         # Real multimodal API call
#         response = model.generate_content([
#             "Analyze this cybersecurity incident screenshot. Extract all visible fraud markers, suspicious URLs, and error messages. Summarize into a technical incident description.", 
#             image_file
#         ])
#         return HttpResponse(json.dumps({'content': response.text}), content_type="application/json")
#     return HttpResponse(status=400)


def api_extract_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            import base64

            image_file = request.FILES['image']
            model = genai.GenerativeModel("gemini-2.5-flash")

            image_bytes = image_file.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            response = model.generate_content([
                "Analyze this cybersecurity screenshot. Extract URLs, suspicious text, and fraud markers. Provide a short technical summary.",
                {
                    "inline_data": {
                        "mime_type": image_file.content_type,
                        "data": image_b64
                    }
                }
            ])

            return JsonResponse({'content': response.text})

        except Exception as e:
            print("AI IMAGE EXTRACT ERROR:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# --- Static Information Views ---

def services_view(request):
    return render(request, 'portal/services.html')

def resources_view(request):
    return render(request, 'portal/resources.html')

def contact_view(request):
    return render(request, 'portal/contact.html')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    return render(request, 'dashboards/admin_dashboard.html')

@login_required
def user_dashboard_view(request):
    """
    User-specific view for tracking incident history and system status.
    """
    my_incidents = Incident.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'incidents': my_incidents,
        'pending_count': my_incidents.filter(status='Pending').count(),
        'resolved_count': my_incidents.filter(status='Resolved').count(),
    }
    return render(request, 'dashboards/user_dashboard.html', context)


@login_required
def profile_settings_view(request):
    """
    Renders the account security and system preference interface.
    Handles the display of current user attributes and saved settings.
    """
    return render(request, 'dashboards/profile.html')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    # 1. Fetch all incidents (Admin sees both User and Anonymous reports)
    incidents = Incident.objects.all().order_by('-created_at')

    # 2. Apply Multi-Parametric Filters
    risk_filter = request.GET.get('risk_level')
    type_filter = request.GET.get('incident_type')
    
    if risk_filter:
        incidents = incidents.filter(risk_level=risk_filter)
    if type_filter:
        incidents = incidents.filter(incident_type=type_filter)

    # 3. Analytics Engine: Count Statistics
    context = {
        'incidents': incidents,
        'total_count': Incident.objects.count(),
        'high_risk_count': Incident.objects.filter(risk_level='HIGH').count(),
        'pending_count': Incident.objects.filter(status='Pending').count(),
        'resolved_count': Incident.objects.filter(status='Resolved').count(),
        
        # Data for Risk Distribution Chart (Pie Chart)
        'risk_data': [
            Incident.objects.filter(risk_level='HIGH').count(),
            Incident.objects.filter(risk_level='MEDIUM').count(),
            Incident.objects.filter(risk_level='LOW').count(),
        ],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def ai_monitor_view(request):
    # Simulated system diagnostics for SIH presentation
    context = {
        'status': 'OPERATIONAL',
        'latency': '240ms',
        'api_usage': Incident.objects.count(), # AI is called for every report
        'model': 'Gemini-1.5-Flash',
        'capabilities': ['Multimodal Image Scan', 'NLP Risk Scoring', 'SOP Generation'],
    }
    return render(request, 'dashboards/ai_monitor.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_analytics_view(request):
    from django.db.models import Count
    
    # Data for Incident Type Trends
    type_counts = Incident.objects.values('incident_type').annotate(total=Count('id'))
    
    context = {
        'labels': [item['incident_type'] for item in type_counts],
        'data': [item['total'] for item in type_counts],
        'high_risk': Incident.objects.filter(risk_level='HIGH').count(),
        'med_risk': Incident.objects.filter(risk_level='MEDIUM').count(),
        'low_risk': Incident.objects.filter(risk_level='LOW').count(),
    }
    return render(request, 'dashboards/analytics.html', context)

@user_passes_test(lambda u: u.is_superuser)
def user_directory_view(request):
    # Use get_user_model() instead of the direct User import
    User = get_user_model()
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboards/user_directory.html', {'users': users})


