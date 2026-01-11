import google.generativeai as genai
import json, base64
from django.http import JsonResponse
from django.conf import settings
from .models import ChatConversation
from django.shortcuts import render

# Global configuration for the Google Gemini API
genai.configure(api_key=settings.AI_API_KEY)

# Use BLOCK_NONE to ensure technical cyber terms aren't flagged as "Harassment" or "Hate Speech"
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]


def full_chat_view(request):
    """Renders the dedicated Full-Screen AI Analysis page."""
    return render(request, 'chatbot/chatbot.html')

def chatbot_query(request):
    """
    API endpoint that automatically detects the user's language 
    and provides a structured safety analysis.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('msg', '')
            image_data = data.get('image', None) 
            
            # Initialize the model confirmed by your console test
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # SYSTEM INSTRUCTION: Automation of Language Mirroring
            # This instruction forces the AI to detect and use the user's input language
            system_prompt = (
                "Role: Indian Cyber Defence AI. "
                "CRITICAL INSTRUCTION: Automatically detect the language of the user input. "
                "You MUST reply in the EXACT SAME language used by the user. "
                "If they ask in Telugu, reply in Telugu. If Hindi, reply in Hindi. "
                "Task: Provide a safety analysis using this EXACT format:\n\n"
                "### 🛡️ RISK LEVEL: [LOW / MEDIUM / HIGH]\n"
                "**Summary:** [One line overview]\n"
                "**Analysis:** [Technical breakdown of the threat]\n"
                "**Action Steps:**\n"
                "1. [Immediate step]\n"
                "2. [Secondary step]"
            )

            # Build the multimodal contents list
            contents = [system_prompt]
            if user_msg:
                contents.append(user_msg)
            if image_data:
                # Structure for multimodal Base64 image input
                contents.append({
                    "mime_type": "image/jpeg",
                    "data": image_data
                })

            # Generate content using the consolidated contents list
            response = model.generate_content(contents)
            bot_reply = response.text

            # Determine language for logging (optional, bot handles detection natively)
            detected_lang = "auto-detected"

            # Persistence for Admin Module Analysis
            ChatConversation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=user_msg if user_msg else "Image/Evidence Scanned",
                response=bot_reply,
                language=detected_lang,
                is_anonymous=not request.user.is_authenticated
            )

            return JsonResponse({'reply': bot_reply})
            
        except Exception as e:
            # Graceful error handling for API or connection issues
            return JsonResponse({'reply': "Intelligence Core error: Secure link interrupted. Please try again."}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)