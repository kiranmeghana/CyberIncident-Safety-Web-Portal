# from django.shortcuts import redirect

# def redirect_user_dashboard(user):
#     if user.is_superuser or user.role == 'admin':
#         return redirect('admin_dashboard')
#     elif user.role == 'student':
#         return redirect('user_dashboard') 
#     else:
#         # Default fallback
#         return redirect('home')