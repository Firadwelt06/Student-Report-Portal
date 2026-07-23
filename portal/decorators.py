from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    return user_passes_test(lambda user: user.is_authenticated and user.is_portal_admin)(view_func)
