import json
import hashlib
from typing import Optional

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse

from charging_system_b2b.settings import IDEMPOTENCY_TTL_SECONDS


UNSAFE_METHODS = {"POST", "PUT", "PATCH"}


def _get_idempotency_key(request) -> Optional[str]:
    return request.META.get("HTTP_IDEMPOTENCY_KEY") or request.headers.get("Idempotency-Key")


def _fingerprint(request) -> str:
    # Use method + path + body to distinguish different operations
    body = request.body or b""
    h = hashlib.sha256()
    h.update(request.method.encode("utf-8"))
    h.update(b"|")
    h.update(request.path.encode("utf-8"))
    h.update(b"|")
    h.update(body)
    return h.hexdigest()


class IdempotencyMiddleware:
    """
    Global idempotency for unsafe methods using an Idempotency-Key header.
    - On first request with a new key: mark as processing, run view, cache the response.
    - On duplicate while processing: return 409 Conflict.
    - On duplicate after completion: return the cached response.
    - On key reuse with different payload: return 409 Conflict.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in UNSAFE_METHODS:
            return self.get_response(request)

        key = _get_idempotency_key(request)
        # If no key provided, pass through — we still rely on DB-level atomicity
        if not key:
            return self.get_response(request)

        fp = _fingerprint(request)
        cache_key = f"idempotency:{key}"
        entry = cache.get(cache_key)

        if entry:
            # Reject key reuse with a different fingerprint
            if entry.get("fingerprint") != fp:
                return HttpResponse(
                    "Idempotency-Key reuse with different payload",
                    status=409,
                )

            status = entry.get("status")
            if status == "processing":
                return HttpResponse("Duplicate request in progress", status=409)
            elif status == "completed":
                payload = entry.get("payload") or {}
                content_type = payload.get("content_type", "application/json")
                status_code = payload.get("status_code", 200)
                content = payload.get("content") or "{}"

                # Rebuild response
                if "application/json" in content_type:
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        data = content
                    return JsonResponse(data, status=status_code, safe=False)
                else:
                    return HttpResponse(content, status=status_code, content_type=content_type)

        # First hit: mark as processing atomically (cache.add succeeds only if missing)
        added = cache.add(cache_key, {"status": "processing", "fingerprint": fp}, timeout=IDEMPOTENCY_TTL_SECONDS)
        if not added:
            # Another request just set it; treat as duplicate in-flight
            return HttpResponse("Duplicate request in progress", status=409)

        # Process the request and cache the final response
        response = self.get_response(request)

        try:
            content = response.content.decode("utf-8") if hasattr(response, "content") else ""
            content_type = response.get("Content-Type", "application/json")
            payload = {
                "status_code": getattr(response, "status_code", 200),
                "content_type": content_type,
                "content": content,
            }
            cache.set(
                cache_key,
                {"status": "completed", "fingerprint": fp, "payload": payload},
                timeout=IDEMPOTENCY_TTL_SECONDS,
            )
        except Exception:
            # If caching fails, we still return the response
            pass

        return response