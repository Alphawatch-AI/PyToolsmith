from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from .types.anthropic_types import (
    AnthropicCacheControlParam,
    AnthropicInputSchema,
    AnthropicToolParam,
)
from .types.bedrock_types import (
    AwsBedrockToolInputSchema,
    AwsBedrockToolParam,
    AwsBedrockToolSchemaJson,
)
from .types.openai_types import (
    OpenAIFunctionDefinition,
    OpenAIFunctionParameters,
    OpenAIToolParam,
)
from .utils import remove_keys


@dataclass
class ToolParameters:
    """Parameters extracted from the tool definition."""

    input_properties: dict[str, Any]
    required_parameters: list[str]
    name: str
    description: str

    def to_bedrock(self, as_dict: bool = True, exclude_fields: list[
        str] = None) -> AwsBedrockToolParam | dict:
        """
        Returns a Bedrock-compatible tool definition.
        `as_dict` set to True will allow you to pass it directly to Bedrock.
        """
        properties = deepcopy(self.input_properties)
        if exclude_fields is not None:
            properties = remove_keys(properties, exclude_fields)

        definitions = properties.pop("definitions", {})

        param = AwsBedrockToolParam(
            name=self.name,
            inputSchema=AwsBedrockToolSchemaJson(
                json=AwsBedrockToolInputSchema(
                    type="object",
                    properties=properties,
                    required=self.required_parameters,
                    definitions=definitions
                )
            ),
            description=self.description,
        )
        if as_dict:
            # Convert to dict - replaces Pydantic's model_dump
            return asdict(param)
        return param

    def to_anthropic(self, use_cache_control: bool = False,
                     exclude_fields: list[str] = None) -> AnthropicToolParam:

        properties = deepcopy(self.input_properties)
        if exclude_fields is not None:
            properties = remove_keys(properties, exclude_fields)

        definitions = properties.pop("definitions", {})

        return AnthropicToolParam(
            name=self.name,
            description=self.description,
            cache_control=AnthropicCacheControlParam(type="ephemeral")
            if use_cache_control
            else None,
            input_schema=AnthropicInputSchema(
                type="object",
                properties=properties,
                required=self.required_parameters,
                definitions=definitions
            ),
        )

    def to_openai(self, *, strict_mode=True,
                  exclude_fields: list[str] = None) -> OpenAIToolParam:
        """
        Strict mode has a better guarantee that the LLM will use the tool correctly. 
        However, it removes additional formatting information and defaults from the 
        LLM's context.
        
        If you want to remove additional keys rom definitions, you can pass them in 
        here as well.
        """

        properties = deepcopy(self.input_properties)
        if strict_mode:
            # We have to remove extra keys such as "format" from the properties...
            properties = remove_keys(
                properties,
                ["format", "default"]
            )
        if exclude_fields:
            properties = remove_keys(properties, exclude_fields)

        return OpenAIToolParam(
            function=OpenAIFunctionDefinition(
                name=self.name,
                description=self.description,
                parameters=OpenAIFunctionParameters(
                    type="object",
                    additionalProperties=not strict_mode,
                    properties=properties,
                    required=list(
                        properties.keys()) if strict_mode else self.required_parameters,
                ),
                strict=strict_mode,
            ),
            type="function"
        )
