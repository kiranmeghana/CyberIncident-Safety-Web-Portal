from django.shortcuts import redirect

def redirect_user_dashboard(user):
    if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
        # This triggers the 'admin_dashboard' URL name, 
        # which calls the view, which loads your template.
        return redirect('admin_dashboard') 
    
    elif hasattr(user, 'role') and user.role == 'user':
        return redirect('user_dashboard')
        
    else:
        return redirect('landing')