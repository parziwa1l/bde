# views/html.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from socialnetwork import api
from socialnetwork.api import _get_social_network_user
from socialnetwork.models import SocialNetworkUsers
from socialnetwork.serializers import PostsSerializer

@require_http_methods(["GET"])
@login_required
def timeline(request):
    keyword = request.GET.get("search", "")
    published = request.GET.get("published", True)
    error = request.GET.get("error", None)

    user = _get_social_network_user(request.user)

    if keyword:
        posts = api.search(keyword, published=published)
    else:
        posts = api.timeline(user, published=published)

    context = {
        "posts": PostsSerializer(posts, many=True).data,
        "searchkeyword": keyword,
        "error": error,
    }

    return render(request, "timeline.html", context)

def _get_social_network_user(user) -> SocialNetworkUsers:
    try:
        return SocialNetworkUsers.objects.get(id=user.id)
    except SocialNetworkUsers.DoesNotExist:
        raise PermissionError("User does not exist")

@require_http_methods(["POST"])
@login_required
def follow(request):
    user = _get_social_network_user(request.user)
    user_to_follow_id = request.POST.get("user_to_follow_id")
    try:
        user_to_follow = SocialNetworkUsers.objects.get(id=user_to_follow_id)
        api.follow(user, user_to_follow)
    except SocialNetworkUsers.DoesNotExist:
        pass
    return redirect("socialnetwork:timeline")

@require_http_methods(["POST"])
@login_required
def unfollow(request):
    user = _get_social_network_user(request.user)
    user_to_unfollow_id = request.POST.get("user_to_unfollow_id")
    try:
        user_to_unfollow = SocialNetworkUsers.objects.get(id=user_to_unfollow_id)
        api.unfollow(user, user_to_unfollow)
    except SocialNetworkUsers.DoesNotExist:
        pass
    return redirect("socialnetwork:timeline")
