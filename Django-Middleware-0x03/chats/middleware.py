from datetime import datetime, timedelta
from django.http import JsonResponse
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(
            f"[{datetime.now()}] {request.method} request to {request.path} from IP: {self.get_client_ip(request)}"
        )
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if not (8 <= current_hour < 17):
            return JsonResponse({
                "error": "⏰ Access is restricted. Only allowed between 8AM and 5PM."
            }, status=403)
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_message_log = defaultdict(list)
        self.limit = 5  # messages
        self.window_seconds = 60  # 1 minute

    def __call__(self, request):
        if request.method == "POST" and "/messages" in request.path:
            ip = self.get_client_ip(request)
            now = datetime.now()

            # Remove timestamps older than the rate limit window
            self.ip_message_log[ip] = [
                ts for ts in self.ip_message_log[ip]
                if now - ts < timedelta(seconds=self.window_seconds)
            ]

            if len(self.ip_message_log[ip]) >= self.limit:
                return JsonResponse({
                    "detail": "❌ Message rate limit exceeded. Only 5 messages per minute allowed."
                }, status=429)

            self.ip_message_log[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ['/messages', '/admin-only-action']
        if any(path in request.path for path in protected_paths):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'detail': 'Authentication required'}, status=401)

            role = getattr(user, 'role', None)
            if role not in ['admin', 'moderator']:
                return JsonResponse({
                    'detail': '❌ Forbidden: You do not have permission to perform this action.'
                }, status=403)

        return self.get_response(request)
