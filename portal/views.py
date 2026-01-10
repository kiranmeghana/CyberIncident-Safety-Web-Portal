import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect

from .models import Incident, ChatLog
from .utils import analyze_cyber_risk

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
    return render(request, 'landing.html')

def report_incident(request):
    """Handles both logged-in and anonymous incident reporting."""
    is_anon_param = request.GET.get('anonymous') == 'true'
    
    if request.method == 'POST':
        itype = request.POST.get('incident_type')
        desc = request.POST.get('description')
        evid = request.FILES.get('evidence')
        
        # Analyze risk using utility function
        score, level, advice = analyze_cyber_risk(desc)
        
        # Save incident to database
        incident = Incident.objects.create(
            user=request.user if request.user.is_authenticated else None,
            incident_type=itype,
            description=desc,
            evidence=evid,
            risk_score=score,
            risk_level=level,
            is_anonymous=is_anon_param or (request.POST.get('is_anonymous') == 'on')
        )
        
        # Dynamic safety guidance
        guidance_map = {
            'Phishing': {'dos': ['Change passwords', 'Enable MFA'], 'donts': ['Click suspicious links']},
            'OTP': {'dos': ['Block bank account immediately'], 'donts': ['Share codes with anyone']},
            'Ransomware': {'dos': ['Disconnect from internet'], 'donts': ['Pay the ransom']},
        }
        current_advice = guidance_map.get(itype, {'dos': ['Report to authorities'], 'donts': ['Delete evidence']})
        
        return render(request, 'portal/recommendations.html', {
            'incident': incident,
            'advice': advice,
            'dos': current_advice['dos'],
            'donts': current_advice['donts']
        })
        
    return render(request, 'portal/report_form.html', {'is_anon': is_anon_param})


# --- AI Chatbot Implementation ---

@csrf_protect
def chatbot_query(request):
    """Universal Gemini-powered chatbot with interaction-based prompts"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_msg = data.get('msg', '')
        active_lang = data.get('lang', 'en')
        
        # interaction_count can be tracked in session to trigger the report prompt
        count = request.session.get('chat_count', 0) + 1
        request.session['chat_count'] = count

        # Gemini API Configuration
        api_key = settings.AI_API_KEY
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Context: You are a Cyber Defence Assistant for the Indian Defence Portal. "
                            f"User is asking in language: {active_lang}. "
                            f"Prompt: {user_msg}. "
                            f"Instructions: Give a concise, professional cyber safety response."
                }]
            }]
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response_data = response.json()
            # Extract text from Gemini response structure
            bot_reply = response_data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            bot_reply = "System is currently busy. Please ensure your internet is connected."

        # Automatic Suggestion Logic (Triggers after 3 pairs)
        if count >= 3:
            suggestion_text = {
                'en': "\n\n**Are you facing a specific issue?** You can [Report Incident](/report) or visit our [Resources](/resources) for guidance.",
                'hi': "\n\n**क्या आप किसी समस्या का सामना कर रहे हैं?** आप [घटना की रिपोर्ट](/report) कर सकते हैं या मार्गदर्शन के लिए हमारे [संसाधन](/resources) देख सकते हैं।",
                'te': "\n\n**మీరు ఏదైనా సమస్యను ఎదుర్కొంటున్నారా?** మీరు [సమస్యను నివేదించవచ్చు](/report) లేదా మార్గదర్శకత్వం కోసం మా [వనరులను](/resources) సందర్శించవచ్చు."
            }
            bot_reply += suggestion_text.get(active_lang, suggestion_text['en'])
            request.session['chat_count'] = 0 # Reset count after prompting

        # [cite_start]Store interaction for Admin [cite: 79, 120]
        ChatLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=user_msg,
            response=bot_reply,
            is_anonymous=not request.user.is_authenticated
        )

        return JsonResponse({'reply': bot_reply})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# --- Static Information Views ---

def services_view(request):
    return render(request, 'portal/services.html')

def resources_view(request):
    return render(request, 'portal/resources.html')

def contact_view(request):
    return render(request, 'portal/contact.html')