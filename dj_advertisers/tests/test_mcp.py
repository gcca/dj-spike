"""Tests for MCP tool registration."""

from django.test import TestCase
from mcp_server import mcp_server
from mcp_server.query_tool import ModelQueryToolsetMeta

from dj_advertisers.models import Advertiser


class AdvertiserMCPRegistrationTest(TestCase):
    """Verify MCP tools are registered for Advertiser."""

    def test_advertiser_query_tool_registered(self):
        """AdvertiserQueryTool is in ModelQueryToolset registry."""
        self.assertIn("AdvertiserQueryTool", ModelQueryToolsetMeta.registry)
        self.assertEqual(
            ModelQueryToolsetMeta.registry["AdvertiserQueryTool"].model,
            Advertiser,
        )

    def test_mcp_server_has_advertiser_tools(self):
        """MCP server exposes Advertiser list, create, update, delete tools."""
        tool_names = [t.name for t in mcp_server._tool_manager._tools.values()]
        expected = [
            "AdvertiserViewSet_ListTool",
            "AdvertiserViewSet_CreateTool",
            "AdvertiserViewSet_UpdateTool",
            "AdvertiserViewSet_DeleteTool",
        ]
        for name in expected:
            self.assertIn(
                name, tool_names, msg=f"Expected tool {name} in {tool_names}"
            )
