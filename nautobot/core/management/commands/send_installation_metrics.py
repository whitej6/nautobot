import hashlib
import platform
import requests
import uuid

from constance import config
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from nautobot.utilities.config import get_settings_or_config


METRICS_ENDPOINT = "https://nautobot.cloud/api/nautobot/installation-metric/"


class Command(BaseCommand):
    help = "Send installation metrics for this Nautobot installation."

    def _hash(self, plaintext):
        return hashlib.sha256(plaintext.encode("utf8")).hexdigest()

    def get_hashed_plugins_with_version(self):
        plugins = {}
        for plugin_name in settings.PLUGINS:
            plugin_name = plugin_name.rsplit(".", 1)[-1]
            plugin_config = apps.get_app_config(plugin_name)
            plugins[self._hash(plugin_name)] = getattr(plugin_config, "version", None)
        plugins = dict(sorted(plugins.items()))

        return plugins

    def handle(self, *args, **options):
        # skip if metrics are disabled
        if not settings.INSTALLATION_METRICS_ENABLED:
            self.stdout.write(
                self.style.WARNING(
                    "Installation metrics are disabled by INSTALLATION_METRICS_ENABLED setting, skipping."
                )
            )
            return

        # get the deployment id for this install from constance or settings
        # if one is not already set, generate a random uuid and set it in constance
        deployment_id = get_settings_or_config("DEPLOYMENT_ID")
        if not deployment_id:
            deployment_id = str(uuid.uuid4())
            config.DEPLOYMENT_ID = deployment_id

        # build the json payload to send
        payload = {
            "deployment_id": deployment_id,
            "nautobot_version": settings.VERSION,
            "python_version": platform.python_version(),
            "installed_apps": self.get_hashed_plugins_with_version(),
            "debug": settings.DEBUG,
        }

        # send the payload to the metrics endpoint
        prepared_request = requests.Request("POST", METRICS_ENDPOINT, json=payload).prepare()
        with requests.Session() as session:
            response = session.send(prepared_request, proxies=settings.HTTP_PROXIES)

        if response.ok:
            self.stdout.write(self.style.SUCCESS(f"Metrics successfully sent to '{METRICS_ENDPOINT}'"))
        else:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to send metrics to '{METRICS_ENDPOINT}'; "
                    f"response status {response.status_code}: {response.content}"
                )
            )
        self.stderr.write(
            "To disable installation metrics, you can set INSTALLATION_METRICS_ENABLED = False in your Nautobot config."
        )
