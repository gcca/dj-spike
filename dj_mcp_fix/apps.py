"""AppConfig for dj_mcp_fix."""

from django.apps import AppConfig
from rest_framework.request import Request
from rest_framework.views import APIView


class DjMcpFixConfig(AppConfig):
    """Restore DRF behavior for non-MCP requests after django-mcp-server patches
    views."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dj_mcp_fix"
    verbose_name = "MCP Fix"

    def ready(self):
        from dj_advertisers.views import AdvertiserViewSet

        original = APIView.initialize_request

        def safe_init(self, request, *args, **kwargs):
            if not hasattr(request, "original_request"):
                return original(self, request, *args, **kwargs)
            # For MCP: request is _DRFRequestWrapper with body. Wrap it in DRF
            # Request so the view receives parsed data; do not return
            # original_request (SimpleNamespace) which has no body.
            parser_context = self.get_parser_context(request)
            return Request(
                request,
                parsers=self.get_parsers(),
                authenticators=self.get_authenticators(),
                negotiator=self.get_content_negotiator(),
                parser_context=parser_context,
            )

        AdvertiserViewSet.initialize_request = safe_init
