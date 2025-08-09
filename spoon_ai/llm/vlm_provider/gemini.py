import json
import os
import time
import base64
from typing import Any, Dict, List, Literal, Optional, Union

from google import genai
from google.genai import types
from pydantic import Field, model_validator
import logging

from spoon_ai.schema import Message
from spoon_ai.llm.base import LLMBase, LLMConfig, LLMResponse
from spoon_ai.llm.factory import LLMFactory

logger = logging.getLogger(__name__)

class GeminiConfig(LLMConfig):
    """Gemini Configuration"""
    
    model: str = "gemini-2.5-pro"
    api_key: str = Field(default_factory=lambda: os.getenv('GEMINI_API_KEY', ''))
    
    @model_validator(mode='after')
    def validate_api_key(self):
        """Validate that API key is provided"""
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required but not set. "
                "Please set the GEMINI_API_KEY environment variable with your Gemini API key."
            )
        return self


@LLMFactory.register("gemini")
class GeminiProvider(LLMBase):
    """Gemini Provider Implementation"""
    
    def __init__(self, config_path: str = "config/config.toml", config_name: str = "chitchat"):
        """Initialize Gemini Provider
        
        Args:
            config_path: Configuration file path
            config_name: Configuration name
            
        Raises:
            ValueError: If GEMINI_API_KEY environment variable is not set
        """
        super().__init__(config_path, config_name)
        
        # Validate API key is available
        if not self.config.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required but not set. "
                "Please set the GEMINI_API_KEY environment variable with your Gemini API key."
            )
        
        # Initialize Gemini API client
        self.client = genai.Client(api_key=self.config.api_key)
    
    def _load_config(self, config_path: str, config_name: str) -> GeminiConfig:
        """Load configuration
        
        Args:
            config_path: Configuration file path
            config_name: Configuration name
            
        Returns:
            GeminiConfig: Gemini configuration
        """
        config = super()._load_config(config_path, config_name)
        return GeminiConfig(**config.model_dump())
    
    async def chat(
        self,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        response_modalities: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat request to Gemini and get response
        
        Args:
            messages: List of messages
            system_msgs: List of system messages
            response_modalities: List of response modalities (optional, e.g. ['Text', 'Image'])
            **kwargs: Other parameters
            
        Returns:
            LLMResponse: LLM response
        """

        
        for msg in messages:
            role = msg.role if hasattr(msg, 'role') else 'unknown'
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if hasattr(msg, 'role') and msg.role == "user":
                user_message = msg.content
                break
        
        # If no user message is found, use system message (if available)
        if not user_message and system_msgs and len(system_msgs) > 0:
            user_message = system_msgs[0].content
            
        # Ensure there is a message to send
        if not user_message:
            user_message = "Hello"
            
        # Get system message content
        system_content = ""
        if system_msgs and len(system_msgs) > 0:
            system_content = " ".join([msg.content for msg in system_msgs])
        
        try:
            # Build request content
            # If content is plain text, convert to Part object
            if isinstance(user_message, str):
                contents = [types.Part.from_text(text=user_message)]
            else:
                # Assume it's already a Part object or other supported type
                contents = [user_message]
            
            # Generate configuration
            generate_config = types.GenerateContentConfig(
                max_output_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # If there are system messages, add to the request
            if system_content:
                generate_config.system_instruction = system_content
            
            # If specific response modalities are needed (e.g. images), add to configuration
            if response_modalities:
                generate_config.response_modalities = response_modalities
                
            # Check if system message contains structured output requirements
            if "IMPORTANT INSTRUCTION" in system_content and "JSON format" in system_content:
                # Set structured output schema
                schema = {
                    "type": "object",
                    "properties": {
                        "response": {
                            "type": "string",
                            "description": "Response content to the user"
                        },
                        "should_hand_off": {
                            "type": "boolean",
                            "description": "Whether the conversation should be handed off to a design expert"
                        }
                    },
                    "required": ["response", "should_hand_off"],
                    "propertyOrdering": ["should_hand_off", "response"]  # Set priority order
                }
                generate_config.response_schema = schema
                generate_config.response_mime_type = 'application/json'  # Set MIME type to JSON
            
            # Send request
            logger.debug(f"Gemini request model: {self.config.model}")

            content = ""
            buffer = ""
            is_content = False
            stream = self.client.models.generate_content_stream(
                model=self.config.model,
                contents=contents,
                config=generate_config
            )

            for part_response in stream:
                chunk = part_response.candidates[0].content.parts[0].text
                buffer += chunk
                if is_content:
                    try:
                        json.loads(buffer)
                        content = json.loads(buffer)["response"]
                        # Compare buffer and content already put in queue, don't include any JSON boundary symbols in final output
                        await self.output_queue.put(chunk.strip("}").strip().strip('"'))
                    except json.JSONDecodeError as e:

                        await self.output_queue.put(chunk)
                        continue
                    except Exception as e:
                        
                        logger.error(f"Gemini API request parsing failed: {str(e)}")
                        logger.error(f"Current buffer: {buffer}")
                        buffer = ""
                        is_content = False
                elif '"response":' in buffer:
                    # Truncate from here, save the following content to content
                    try:
                        parts = buffer.split('"response":', 1)
                        if len(parts) > 1:
                            chunk = parts[1].strip()
                            is_content = True
                            await self.output_queue.put(chunk.strip("}").strip().strip('"'))
                            
                    except Exception as e:
                        logger.error(f"Gemini API request parsing failed: {str(e)}")
                        logger.error(f"Current buffer: {buffer}")
                        buffer = ""
                        is_content = False
            await self.output_queue.put(None)
            self.task_done.set()
            return LLMResponse(content=content, text=buffer)
        except Exception as e:
            error_msg = f"Gemini API request failed: {str(e)}"
            logger.error(error_msg)
            return LLMResponse(content=f"API request failed: {str(e)}", text=f"API request failed: {str(e)}")
    
    async def completion(self, prompt: str, **kwargs) -> LLMResponse:
        """Send text completion request to Gemini and get response
        
        Args:
            prompt: Prompt text
            **kwargs: Other parameters
            
        Returns:
            LLMResponse: LLM response
        """
        # Create a user message
        message = Message.user_message(prompt)
        
        # Use chat method
        return await self.chat(
            messages=[message],
            **kwargs
        )
    
    async def chat_with_tools(
        self,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        **kwargs
    ) -> LLMResponse:
        """Send chat request to Gemini that may contain tool calls and get response
        
        Note: Gemini currently doesn't support tool calls, this method will use regular chat method
        
        Args:
            messages: List of messages
            system_msgs: List of system messages
            tools: List of tools (not supported by Gemini)
            tool_choice: Tool choice mode (not supported by Gemini)
            **kwargs: Other parameters
            
        Returns:
            LLMResponse: LLM response
        """
        logger.warning("Gemini currently doesn't support tool calls, will use regular chat method")
        
        # If there are tool definitions, they can be added to system messages
        if tools and system_msgs:
            tools_desc = "Available tools:\n"
            for tool in tools:
                if 'function' in tool:
                    func = tool['function']
                    tools_desc += f"- {func.get('name', 'unknown')}: {func.get('description', 'No description')}\n"
            
            # Add tool description to system messages
            new_system_msgs = system_msgs.copy()
            new_system_msgs.append(Message.system_message(tools_desc))
            return await self.chat(messages=messages, system_msgs=new_system_msgs, **kwargs)
        
        # If no tools, use regular chat method directly
        return await self.chat(messages=messages, system_msgs=system_msgs, **kwargs)
    
    async def generate_content(
        self,
        model: Optional[str] = None,
        contents: Union[str, List, types.Content, types.Part] = None,
        config: Optional[types.GenerateContentConfig] = None,
        **kwargs
    ) -> LLMResponse:
        """Directly call Gemini's generate_content interface
        
        Args:
            model: Model name (optional, will override model in configuration)
            contents: Request content, can be string, list, or types.Content/types.Part object
            config: Generation configuration
            **kwargs: Other parameters
            
        Returns:
            LLMResponse: LLM response
        """
        # Use provided model or model from configuration
        model_name = model if model else self.config.model
        
        # If no configuration is provided, create a default one
        if not config:
            config = types.GenerateContentConfig(
                max_output_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
        try:
            # Log request information
            logger.info(f"Gemini generate_content request model: {model_name}")
            
            # Send request
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            
            logger.debug(f"Gemini response: {response}")
            
            # Parse response
            content = ""
            response_text = ""
            image_data = None
            
            # Check if there are candidate results
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    # Iterate through all parts
                    for part in candidate.content.parts:
                        # Check if there is text content
                        if hasattr(part, "text") and part.text:
                            if content:
                                content += "\n" + part.text
                            else:
                                content = part.text
                            response_text = content
                        # Check if there is image content
                        elif hasattr(part, "inline_data"):
                            # Save image data
                            image_data = {
                                "mime_type": getattr(part.inline_data, "mime_type", "image/jpeg"),
                                "data": getattr(part.inline_data, "data", b"")
                            }
                            logger.info(f"Image response detected, MIME type: {image_data['mime_type']}")
                            
                            # Save image to local storage
                            # Create directory (if it doesn't exist)
                            output_dir = "runtime-image-output"
                            os.makedirs(output_dir, exist_ok=True)
                            
                            # Generate unique filename
                            timestamp = int(time.time())
                            ext = image_data['mime_type'].split('/')[-1]
                            filename = f"gemini_image_{timestamp}.{ext}"
                            filepath = os.path.join(output_dir, filename)
                            
                            # Save image
                            try:
                                with open(filepath, "wb") as f:
                                    f.write(image_data['data'])
                                logger.info(f"Image saved to: {filepath}")
                                
                                # Add image path to response
                                image_info = {
                                    "filepath": filepath,
                                    "mime_type": image_data['mime_type']
                                }
                                
                                # Create an image path list for LLMResponse
                                image_paths = []
                                image_paths.append(image_info)
                                
                                # Add image information to text response
                                if content:
                                    content += f"\n[Generated image saved to: {filepath}]"
                                else:
                                    content = f"[Generated image saved to: {filepath}]"
                                response_text = content
                                
                            except Exception as e:
                                logger.error(f"Failed to save image: {str(e)}")
            
            # If no content was obtained from candidates, try using the text attribute
            if not content and not image_data and hasattr(response, "text"):
                response_text = response.text
                content = response_text
            
            # If there is image data, add it to the response
            tool_calls = []
            image_paths = []
            if image_data:
                tool_calls.append({
                    "type": "image",
                    "image": {
                        "mime_type": image_data["mime_type"],
                        "data": image_data["data"]
                    }
                })
                # If image paths were saved in previous processing, add them to image_paths
                if 'image_paths' in locals() and image_paths:
                    image_paths = image_paths
            
            return LLMResponse(content=content or "【Image response】", text=response_text, tool_calls=tool_calls, image_paths=image_paths)
        except Exception as e:
            error_msg = f"Gemini API request failed: {str(e)}"
            logger.error(error_msg)
            return LLMResponse(content=f"API request failed: {str(e)}", text=f"API request failed: {str(e)}", tool_calls=[]) 