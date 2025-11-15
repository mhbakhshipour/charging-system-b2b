import requests
import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

LOGGER = logging.getLogger(__name__)

EXTERNAL_API_URLS = {}


def check_database():
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
        return True, None
    except Exception as e:
        return False, str(e)


def check_cache():
    try:
        cache.set("health_check", "ok", timeout=1)
        return cache.get("health_check") == "ok", None
    except Exception as e:
        return False, str(e)


def check_external_apis():
    results = []
    errors = []
    for name, url in EXTERNAL_API_URLS.items():
        try:
            response = requests.get(url, timeout=5)
            results.append({"name": name, "health": response.status_code == 200})
        except Exception as e:
            results.append({"name": name, "health": False})
            errors.append({"name": name, "error": str(e)})
    return results, errors


def health_check(request):
    health_status = {
        "database": False,
        "cache": False,
        "external_api": [],
        "status": "unhealthy",
    }
    health_status_error = {"database": None, "cache": None, "external_api": []}

    # Check database
    health_status["database"], health_status_error["database"] = check_database()

    # Check cache
    health_status["cache"], health_status_error["cache"] = check_cache()

    # Check external APIs
    health_status["external_api"], api_errors = check_external_apis()
    health_status_error["external_api"].extend(api_errors)

    # Overall status
    health_status["status"] = (
        "healthy"
        if health_status["database"]
        and health_status["cache"]
        and all(api["health"] for api in health_status["external_api"])
        else "unhealthy"
    )

    # Log errors if any
    if any(health_status_error.values()):
        LOGGER.error("Health check errors: %s", health_status_error)

    return JsonResponse(health_status)
