"""
Anthropic Provider implementation for the unified LLM interface.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from logging import getLogger

from anthropic import AsyncAnthropic
from httpx import AsyncClient

from spoon_ai.schema import Message, ToolCall, Function
from ..interface import LLMProviderInterface, LLMResponse, ProviderMetadata, ProviderCapability
from ..errors import ProviderError, AuthenticationError, RateLimitError, ModelNotFoundError, NetworkError
from ..registry import register_provider

logger = getLogger(__name__)


@register_provider("anthropic", [
    ProviderCapability.CHAT,
    ProviderCapability.COMPLETION,
    ProviderCapability.TOOLS,
    ProviderCapability.STREAMING
])
class AnthropicProvider(LLMProviderInterface):
    """Anthropic provider implementation."""
    
    def __init__(self):
        self.client: Optional[AsyncAnthropic] = None
        self.config: Dict[str, Any] = {}
        self.model: str = ""
        self.max_tokens: int = 4096
        self.temperature: float = 0.3
        self.enable_prompt_cache: bool = True
        self.cache_metrics = {
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
            "total_input_tokens": 0
        }
        
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the Anthropic provider with configuration."""
        try:
            self.config = config
            self.model = config.get('model', 'claude-sonnet-4-20250514')
            self.max_tokens = config.get('max_tokens', 4096)
            self.temperature = config.get('temperature', 0.3)
            self.enable_prompt_cache = config.get('enable_prompt_cache', True)
            
            api_key = config.get('api_key')
            if not api_key:
                raise AuthenticationError("anthropic", context={"config": config})
            
            timeout = config.get('timeout', 30)
            http_client = AsyncClient(follow_redirects=True, timeout=timeout)
            
            self.client = AsyncAnthropic(
                api_key=api_key,
                http_client=http_client
            )
            
            logger.info(f"Anthropic provider initialized with model: {self.model}")
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ProviderError)):
                raise
            raise ProviderError("anthropic", f"Failed to initialize: {str(e)}", original_error=e)
    
    def _convert_messages(self, messages: List[Message]) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """Convert Message objects to Anthropic format, separating system messages."""
        system_content = None
        anthropic_messages = []
        
        for message in messages:
            if message.role == "system":
                # Handle system messages separately
                # Only apply cache_control to system message if it's large enough
                if (self.enable_prompt_cache and 
                    len(message.content) >= 4000):
                    system_content = [
                        {
                            "type": "text",
                            "text": message.content,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                    logger.info(f"Applied cache_control to system message ({len(message.content)} chars)")
                else:
                    # Use string format for simple system messages
                    system_content = message.content
            elif message.role == "tool":
                # Convert tool messages to user messages with tool_result
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": message.tool_call_id,
                        "content": message.content
                    }]
                })
            elif message.role == "assistant":
                content = []
                
                # Add text content if present
                if message.content:
                    content.append({
                        "type": "text",
                        "text": message.content
                    })
                
                # Add tool calls if present
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        try:
                            arguments = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        content.append({
                            "type": "tool_use",
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "input": arguments
                        })
                
                anthropic_messages.append({
                    "role": "assistant",
                    "content": content if content else message.content
                })
            elif message.role == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": message.content
                })
        
        return system_content, anthropic_messages
    
    def _convert_tools(self, tools: List[Dict]) -> List[Dict]:
        """Convert tools to Anthropic format."""
        anthropic_tools = []
        cache_control_count = 0
        max_cache_control_blocks = 3  # Leave room for system message cache_control
        
        for i, tool in enumerate(tools):
            anthropic_tool = {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"]
            }
            
            # Only add cache control to the first few tools to stay within Anthropic's limit
            # Prioritize tools with larger schemas or descriptions
            tool_size = len(str(tool["function"]["parameters"])) + len(tool["function"]["description"])
            should_cache = (
                self.enable_prompt_cache and 
                cache_control_count < max_cache_control_blocks and
                len(tools) > 4 and  # Only use cache_control when there are many tools
                (tool_size > 500 or i < 2)  # Cache large tools or first 2 tools
            )
            
            if should_cache:
                anthropic_tool["cache_control"] = {"type": "ephemeral"}
                cache_control_count += 1
                logger.debug(f"Applied cache_control to tool: {tool['function']['name']} (size: {tool_size})")
            
            anthropic_tools.append(anthropic_tool)
        
        if cache_control_count > 0:
            logger.info(f"Applied cache_control to {cache_control_count}/{len(tools)} tools")
        
        return anthropic_tools
    
    def _log_cache_metrics(self, usage_data) -> None:
        """Log cache metrics from Anthropic API response usage data."""
        if self.enable_prompt_cache and usage_data:
            if hasattr(usage_data, 'cache_creation_input_tokens') and usage_data.cache_creation_input_tokens:
                self.cache_metrics["cache_creation_input_tokens"] += usage_data.cache_creation_input_tokens
                logger.info(f"Cache creation tokens: {usage_data.cache_creation_input_tokens}")
            if hasattr(usage_data, 'cache_read_input_tokens') and usage_data.cache_read_input_tokens:
                self.cache_metrics["cache_read_input_tokens"] += usage_data.cache_read_input_tokens
                logger.info(f"Cache read tokens: {usage_data.cache_read_input_tokens}")
            if hasattr(usage_data, 'input_tokens') and usage_data.input_tokens:
                self.cache_metrics["total_input_tokens"] += usage_data.input_tokens
    
    def get_cache_metrics(self) -> Dict[str, int]:
        """Get current cache performance metrics."""
        return self.cache_metrics.copy()
    
    async def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Send chat request to Anthropic."""
        if not self.client:
            raise ProviderError("anthropic", "Provider not initialized")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            system_content, anthropic_messages = self._convert_messages(messages)
            
            # Extract parameters
            model = kwargs.get('model', self.model)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            temperature = kwargs.get('temperature', self.temperature)
            
            # Prepare request parameters
            request_params = {
                'model': model,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': anthropic_messages,
                **{k: v for k, v in kwargs.items() if k not in ['model', 'max_tokens', 'temperature']}
            }
            
            # Only add system parameter if we have system content
            if system_content is not None:
                request_params['system'] = system_content
            
            response = await self.client.messages.create(**request_params)
            
            duration = asyncio.get_event_loop().time() - start_time
            
            # Log cache metrics
            if hasattr(response, 'usage'):
                self._log_cache_metrics(response.usage)
            
            return self._convert_response(response, duration)
            
        except Exception as e:
            await self._handle_error(e)
    
    async def chat_stream(self, messages: List[Message], **kwargs) -> AsyncGenerator[str, None]:
        """Send streaming chat request to Anthropic."""
        if not self.client:
            raise ProviderError("anthropic", "Provider not initialized")
        
        try:
            system_content, anthropic_messages = self._convert_messages(messages)
            
            # Extract parameters
            model = kwargs.get('model', self.model)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            temperature = kwargs.get('temperature', self.temperature)
            
            # Prepare request parameters
            request_params = {
                'model': model,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': anthropic_messages,
                **{k: v for k, v in kwargs.items() if k not in ['model', 'max_tokens', 'temperature']}
            }
            
            # Only add system parameter if we have system content
            if system_content is not None:
                request_params['system'] = system_content
            
            async with self.client.messages.stream(**request_params) as stream:
                async for chunk in stream:
                    if chunk.type == "content_block_delta" and chunk.delta.type == "text_delta":
                        yield chunk.delta.text
                    elif chunk.type == "message_start":
                        # Log cache metrics from streaming message_start event
                        if hasattr(chunk, 'message') and hasattr(chunk.message, 'usage'):
                            self._log_cache_metrics(chunk.message.usage)
                            
        except Exception as e:
            await self._handle_error(e)
    
    async def completion(self, prompt: str, **kwargs) -> LLMResponse:
        """Send completion request to Anthropic."""
        # Convert to chat format
        messages = [Message(role="user", content=prompt)]
        return await self.chat(messages, **kwargs)
    
    async def chat_with_tools(self, messages: List[Message], tools: List[Dict], **kwargs) -> LLMResponse:
        """Send chat request with tools to Anthropic."""
        if not self.client:
            raise ProviderError("anthropic", "Provider not initialized")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            system_content, anthropic_messages = self._convert_messages(messages)
            anthropic_tools = self._convert_tools(tools)
            
            # Extract parameters
            model = kwargs.get('model', self.model)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            temperature = kwargs.get('temperature', self.temperature)
            
            # Use streaming for tool calls to handle complex responses
            content = ""
            buffer = ""
            buffer_type = ""
            current_tool = None
            tool_calls = []
            finish_reason = None
            native_finish_reason = None
            
            # Prepare request parameters
            request_params = {
                'model': model,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': anthropic_messages,
                'tools': anthropic_tools,
                **{k: v for k, v in kwargs.items() if k not in ['model', 'max_tokens', 'temperature']}
            }
            
            # Only add system parameter if we have system content
            if system_content is not None:
                request_params['system'] = system_content
            
            async with self.client.messages.stream(**request_params) as stream:
                async for chunk in stream:
                    if chunk.type == "message_start":
                        # Log cache metrics from streaming message_start event
                        if hasattr(chunk, 'message') and hasattr(chunk.message, 'usage'):
                            self._log_cache_metrics(chunk.message.usage)
                        continue
                    elif chunk.type == "message_delta":
                        # Extract finish_reason from message delta
                        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'stop_reason'):
                            finish_reason = chunk.delta.stop_reason
                            native_finish_reason = chunk.delta.stop_reason
                        continue
                    elif chunk.type == "message_stop":
                        # Extract finish_reason from message stop
                        if hasattr(chunk, 'message') and hasattr(chunk.message, 'stop_reason'):
                            finish_reason = chunk.message.stop_reason
                            native_finish_reason = chunk.message.stop_reason
                        continue
                    elif chunk.type in ["text", "input_json"]:
                        continue
                    elif chunk.type == "content_block_start":
                        buffer_type = chunk.content_block.type
                        if buffer_type == "tool_use":
                            current_tool = {
                                "id": chunk.content_block.id,
                                "function": {
                                    "name": chunk.content_block.name,
                                    "arguments": {}
                                }
                            }
                        continue
                    elif chunk.type == "content_block_delta" and chunk.delta.type == "text_delta":
                        buffer += chunk.delta.text
                        continue
                    elif chunk.type == "content_block_delta" and chunk.delta.type == "input_json_delta":
                        buffer += chunk.delta.partial_json
                    elif chunk.type == "content_block_stop":
                        content += buffer
                        if buffer_type == "tool_use" and current_tool:
                            current_tool["function"]["arguments"] = buffer
                            tool_call = ToolCall(
                                id=current_tool["id"],
                                type="function",
                                function=Function(
                                    name=current_tool["function"]["name"],
                                    arguments=current_tool["function"]["arguments"]
                                )
                            )
                            tool_calls.append(tool_call)
                        buffer = ""
                        buffer_type = ""
                        current_tool = None
            
            duration = asyncio.get_event_loop().time() - start_time
            
            # Map Anthropic stop reasons to standard finish reasons
            if finish_reason == "end_turn":
                finish_reason = "stop"
            elif finish_reason == "max_tokens":
                finish_reason = "length"
            elif finish_reason == "tool_use":
                finish_reason = "tool_calls"
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=model,
                finish_reason=finish_reason,
                native_finish_reason=native_finish_reason,
                tool_calls=tool_calls,
                duration=duration,
                metadata={"cache_metrics": self.cache_metrics}
            )
            
        except Exception as e:
            await self._handle_error(e)
    
    def _convert_response(self, response, duration: float) -> LLMResponse:
        """Convert Anthropic response to standardized LLMResponse."""
        content = ""
        if response.content:
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
        
        # Extract usage information
        usage = None
        if hasattr(response, 'usage'):
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        
        # Map stop reasons
        finish_reason = response.stop_reason
        if finish_reason == "end_turn":
            standardized_finish_reason = "stop"
        elif finish_reason == "max_tokens":
            standardized_finish_reason = "length"
        elif finish_reason == "tool_use":
            standardized_finish_reason = "tool_calls"
        else:
            standardized_finish_reason = finish_reason
        
        return LLMResponse(
            content=content,
            provider="anthropic",
            model=response.model,
            finish_reason=standardized_finish_reason,
            native_finish_reason=response.stop_reason,
            usage=usage,
            duration=duration,
            metadata={
                "response_id": response.id,
                "cache_metrics": self.cache_metrics
            }
        )
    
    def get_metadata(self) -> ProviderMetadata:
        """Get Anthropic provider metadata."""
        return ProviderMetadata(
            name="anthropic",
            version="1.0.0",
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.COMPLETION,
                ProviderCapability.TOOLS,
                ProviderCapability.STREAMING
            ],
            max_tokens=200000,  # Claude-3 context limit
            supports_system_messages=True,
            rate_limits={
                "requests_per_minute": 1000,
                "tokens_per_minute": 40000
            }
        )
    
    async def health_check(self) -> bool:
        """Check if Anthropic provider is healthy."""
        if not self.client:
            return False
        
        try:
            # Simple test request
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.warning(f"Anthropic health check failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup Anthropic provider resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("Anthropic provider cleaned up")
    
    async def _handle_error(self, error: Exception) -> None:
        """Handle and convert Anthropic errors to standardized errors."""
        error_str = str(error).lower()
        
        if "authentication" in error_str or "api key" in error_str:
            raise AuthenticationError("anthropic", context={"original_error": str(error)})
        elif "rate limit" in error_str:
            raise RateLimitError("anthropic", context={"original_error": str(error)})
        elif "model" in error_str and "not found" in error_str:
            raise ModelNotFoundError("anthropic", self.model, context={"original_error": str(error)})
        elif "timeout" in error_str or "connection" in error_str:
            raise NetworkError("anthropic", "Network error", original_error=error)
        else:
            raise ProviderError("anthropic", f"Request failed: {str(error)}", original_error=error)