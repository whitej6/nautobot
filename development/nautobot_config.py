"""Nautobot development configuration file."""
import os

from nautobot.core.settings import *  # noqa: F403
from nautobot.core.settings_funcs import is_truthy

#
# Debugging defaults to True rather than False for the development environment
#
DEBUG = is_truthy(os.getenv("NAUTOBOT_DEBUG", "True"))

# Django Debug Toolbar - enabled only when debugging
if DEBUG:
    if "debug_toolbar" not in INSTALLED_APPS:  # noqa: F405
        INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
    if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    # By default the toolbar only displays when the request is coming from one of INTERNAL_IPS.
    # For the Docker dev environment, we don't know in advance what that IP may be, so override to skip that check
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: DEBUG}

#
# Logging for the development environment, taking into account the redefinition of DEBUG above
#

LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOGGING["loggers"]["nautobot"]["handlers"] = ["verbose_console" if DEBUG else "normal_console"]  # noqa: F405
LOGGING["loggers"]["nautobot"]["level"] = LOG_LEVEL  # noqa: F405

#
# Plugins
#

PLUGINS = [
    "example_plugin",
]


#
# Development Environment for SSO
# Configure `invoke.yml` based on example for SSO development environment
#

# OIDC Dev ENV
if is_truthy(os.getenv("ENABLE_OIDC", "False")):
    import requests

    AUTHENTICATION_BACKENDS = (
        "social_core.backends.keycloak.KeycloakOAuth2",
        "nautobot.core.authentication.ObjectPermissionBackend",
    )
    SOCIAL_AUTH_KEYCLOAK_KEY = "nautobot"
    SOCIAL_AUTH_KEYCLOAK_SECRET = "7b1c3527-8702-4742-af69-2b74ee5742e8"
    SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY = requests.get("http://keycloak:8087/realms/nautobot/", timeout=15).json()[
        "public_key"
    ]
    SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL = "http://localhost:8087/realms/nautobot/protocol/openid-connect/auth"
    SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL = "http://keycloak:8087/realms/nautobot/protocol/openid-connect/token"
    SOCIAL_AUTH_KEYCLOAK_VERIFY_SSL = False

METRICS_ENABLED = True

CELERY_WORKER_PROMETHEUS_PORTS = [8080]
