from django.http import JsonResponse
from ..accounts.models import User
from ..utils import login_required_session


@login_required_session
def modify_data(request):
    user = User.objects.get(email=request.session["user_email"])
    modified_name = request.GET.get("name", user.name)

    if modified_name != user.name:
        user.name = modified_name
        user.save()

    return JsonResponse({'success': True})
