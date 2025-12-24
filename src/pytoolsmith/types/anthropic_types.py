from dataclasses import dataclass
from typing import Literal


@dataclass
class AnthropicCacheControlParam:
    type: Literal["ephemeral"]


@dataclass
class AnthropicInputSchema:
    type: Literal["object"]
    required: list[str]
    properties: dict
    """The input properties"""
    definitions: dict


@dataclass
class AnthropicToolParam:
    input_schema: AnthropicInputSchema
    name: str
    description: str
    cache_control: AnthropicCacheControlParam | None = None


@dataclass
class AnthropicUserLocation:
    """Location information for localizing web search results."""

    type: Literal["approximate"] = "approximate"
    city: str | None = None
    region: str | None = None
    country: str | None = None
    timezone: str | None = None


@dataclass
class AnthropicWebSearchToolParam:
    """
    Anthropic's built-in web search tool configuration.

    See: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool

    Supported models: Claude Sonnet 4.5, Sonnet 4, Haiku 4.5, Opus 4.5, Opus 4.1, Opus 4
    """

    type: Literal["web_search_20250305"] = "web_search_20250305"
    name: Literal["web_search"] = "web_search"
    max_uses: int = 5
    """Maximum number of web searches allowed per request."""
    allowed_domains: list[str] | None = None
    """Only include results from these domains."""
    blocked_domains: list[str] | None = None
    """Never include results from these domains."""
    user_location: AnthropicUserLocation | None = None
    """Localize search results based on user location."""

    def to_dict(self) -> dict:
        """Convert to dict format for API request, excluding None values."""
        result: dict = {
            "type": self.type,
            "name": self.name,
            "max_uses": self.max_uses,
        }
        if self.allowed_domains:
            result["allowed_domains"] = self.allowed_domains
        if self.blocked_domains:
            result["blocked_domains"] = self.blocked_domains
        if self.user_location:
            location_dict = {"type": self.user_location.type}
            if self.user_location.city:
                location_dict["city"] = self.user_location.city
            if self.user_location.region:
                location_dict["region"] = self.user_location.region
            if self.user_location.country:
                location_dict["country"] = self.user_location.country
            if self.user_location.timezone:
                location_dict["timezone"] = self.user_location.timezone
            result["user_location"] = location_dict
        return result
