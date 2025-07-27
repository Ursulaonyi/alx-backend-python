from datetime import datetime
import logging
from django.http import HttpResponseForbidden

# Configure logging to file
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_entry)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        start_time = datetime.strptime("18:00", "%H:%M").time()  # 6 PM
        end_time = datetime.strptime("21:00", "%H:%M").time()    # 9 PM

        if not (start_time <= now <= end_time):
            return HttpResponseForbidden("❌ Access denied: You can only access the chat between 6:00 PM and 9:00 PM.")

        return self.get_response(request)
