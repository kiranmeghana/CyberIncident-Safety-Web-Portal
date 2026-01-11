def base_template(request):
    """
    Globally provides the correct base template path based on login status.
    Used for SIH25183 dynamic UI switching.
    """
    if request.user.is_authenticated:
        return {"base_template": "base2.html"}
    return {"base_template": "base1.html"}