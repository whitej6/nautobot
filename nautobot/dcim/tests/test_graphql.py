from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from nautobot.core.graphql import execute_query
from nautobot.dcim.models import Device, DeviceType, DeviceRole, Manufacturer, Platform, Site
from nautobot.extras.models import DynamicGroup
from nautobot.utilities.testing import create_test_user, TestCase


class GraphQLTestCase(TestCase):
    def setUp(self):
        self.user = create_test_user("graphql_testuser")
        self.site = Site.objects.first()
        self.device_role = DeviceRole.objects.create(name="Switch")
        self.manufacturer = Manufacturer.objects.create(name="Brand")
        self.platform = Platform.objects.create(name="Platform", network_driver="cisco_ios")
        self.device_type = DeviceType.objects.create(model="Model", manufacturer=self.manufacturer)
        self.device = Device.objects.create(
            site=self.site,
            device_role=self.device_role,
            device_type=self.device_type,
            name="Device",
            platform=self.platform,
        )
        self.dynamic_group = DynamicGroup.objects.create(
            name="Dynamic_Group", content_type=ContentType.objects.get_for_model(Device)
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_execute_query(self):
        with self.subTest("device dynamic groups query"):
            query = "query {devices {name dynamic_groups {name}}}"
            resp = execute_query(query, user=self.user).to_dict()
            self.assertFalse(resp["data"].get("error"))
            self.assertEqual(resp["data"]["devices"][0]["dynamic_groups"][0]["name"], self.dynamic_group.name)

        with self.subTest("device platform drivers query"):
            query = "query {devices {platform {network_driver network_driver_mappings}}}"
            resp = execute_query(query, user=self.user).to_dict()
            self.assertFalse(resp["data"].get("error"))
            self.assertEqual(resp["data"]["devices"][0]["platform"]["network_driver"], "cisco_ios")
            self.assertEqual(
                resp["data"]["devices"][0]["platform"]["network_driver_mappings"]["ansible"], "cisco.ios.ios"
            )
            self.assertEqual(resp["data"]["devices"][0]["platform"]["network_driver_mappings"]["netmiko"], "cisco_ios")
            self.assertEqual(
                resp["data"]["devices"][0]["platform"]["network_driver_mappings"]["scrapli"], "cisco_iosxe"
            )
