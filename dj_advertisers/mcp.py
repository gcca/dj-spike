"""MCP tools for Advertiser model and AdvertiserViewSet."""

from mcp_server import (
    ModelQueryToolset,
    drf_publish_create_mcp_tool,
    drf_publish_destroy_mcp_tool,
    drf_publish_list_mcp_tool,
    drf_publish_update_mcp_tool,
)

from .models import Advertiser
from .views import AdvertiserViewSet


class AdvertiserQueryTool(ModelQueryToolset):
    """Query tool for Advertiser model.

    List and filter advertisers.
    """

    model = Advertiser

    extra_instructions = (
        "Use this tool to list advertisers with optional filters. "
        "Supports filters: name, monetization_type, billing_source, billing_timezone, "
        "discount, default_conversion_rate, created_at, updated_at."
    )


LIST_INSTRUCTIONS = (
    "List advertisers. Supports optional query filters (name, monetization_type, "
    "billing_source, billing_timezone, discount, default_conversion_rate, "
    "created_at_after, created_at_before, etc.). Returns a list of advertiser objects."
)
CREATE_INSTRUCTIONS = (
    "Create a new advertiser. Provide: name (required), and optionally discount, "
    "default_conversion_rate, monetization_type (CPC|CPA), billing_source (INTERNAL|PARTNER), "
    "billing_timezone (UTC|EST|CST|PST)."
)
UPDATE_INSTRUCTIONS = (
    "Update an existing advertiser by id. Provide id and fields to update: name, "
    "discount, default_conversion_rate, monetization_type, billing_source, billing_timezone."
)
DESTROY_INSTRUCTIONS = "Delete an advertiser by id."

drf_publish_list_mcp_tool(
    AdvertiserViewSet, instructions=LIST_INSTRUCTIONS, actions={"get": "list"}
)
drf_publish_create_mcp_tool(
    AdvertiserViewSet,
    instructions=CREATE_INSTRUCTIONS,
    actions={"post": "create"},
)
drf_publish_update_mcp_tool(
    AdvertiserViewSet,
    instructions=UPDATE_INSTRUCTIONS,
    actions={"put": "update"},
)
drf_publish_destroy_mcp_tool(
    AdvertiserViewSet,
    instructions=DESTROY_INSTRUCTIONS,
    actions={"delete": "destroy"},
)
