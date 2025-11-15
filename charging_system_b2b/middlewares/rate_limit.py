from django.core.cache import cache
from django.http import HttpResponseForbidden

from charging_system_b2b.settings import (
    UNSAFE_METHOD_RATE_LIMIT_NUMBER,
    UNSAFE_METHOD_RATE_LIMIT_DURATION,
)


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Not apply rate limiting to safe methods
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return self.get_response(request)

        # Get the client's IP address
        client_ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get(
            "REMOTE_ADDR"
        )

        # Define the rate limit parameters
        rate_number = UNSAFE_METHOD_RATE_LIMIT_NUMBER
        rate_duration = UNSAFE_METHOD_RATE_LIMIT_DURATION
        cache_key = f"rate_limit:{client_ip}:{request.path}"

        # Get the current number of requests made by the client
        current_requests = cache.get(cache_key, 0)

        # Check if the client has exceeded the rate limit
        if current_requests >= rate_number:
            return HttpResponseForbidden("Rate limit exceeded")

        # Update the number of requests made by the client
        cache.set(cache_key, current_requests + 1, rate_duration)

        # Pass the request through to the next middleware
        response = self.get_response(request)

        return response
