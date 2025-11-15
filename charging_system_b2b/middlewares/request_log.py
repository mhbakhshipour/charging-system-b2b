import logging
from django.utils.deprecation import MiddlewareMixin

import socket
from datetime import datetime
import json

request_logger = logging.getLogger("django.request")


class RequestLogMiddleware(MiddlewareMixin):
    exclude_url = ["/api-token-auth/", "/api-auth/", "/admin/"]
    method_allowed = ["POST", "PUT", "PATCH"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_request(self, request):
        if request.method in self.method_allowed:
            request.req_body = request.body

    def extract_log_info(self, request, response=None, exception=None):
        log_data = {
            "remote_address": request.META.get("HTTP_X_REAL_IP", "127.0.0.1"),
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "request_date_time": str(datetime.now()),
            "user": request.user.username if request.user.is_authenticated else "ann",
        }

        try:
            log_data["request_body"] = json.loads(str(request.body, "utf-8"))
        except:
            log_data["request_body"] = "UNKNOWN"

        if response:
            try:
                log_data["response_body"] = json.loads(response.content)
            except:
                pass
        return log_data

    def process_response(self, request, response):
        if not any(i in str(request.get_full_path()) for i in self.exclude_url):
            if not str(response.status_code).startswith("2"):
                log_data = self.extract_log_info(
                    request=request, response=response)
                request_logger.error(json.dumps(log_data))
        return response
