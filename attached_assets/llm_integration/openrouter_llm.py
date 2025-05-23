"""
OpenRouter LLM integration for AI GM Brain system
"""

import openai
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Dict, Any
import requests
import json
import time
from datetime import datetime

class OpenRouterLLM(LLM):
    """OpenRouter LLM implementation for Langchain"""
    
    api_key: str
    model: str = "anthropic/claude-3-sonnet"
    base_url: str = "https://openrouter.ai/api/v1"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3-sonnet", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.model = model
    
    @property
    def _llm_type(self) -> str:
        return "openrouter"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-gm-brain.com",  # Replace with your site
            "X-Title": "AI GM Brain"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stop": stop
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            raise Exception(f"OpenRouter API error: {e}")

class EnhancedLLMManager:
    """Enhanced LLM manager with OpenRouter integration and database tracking"""
    
    def __init__(self, api_key: str, db_service, default_model: str = "anthropic/claude-3-sonnet"):
        self.api_key = api_key
        self.db_service = db_service
        self.default_model = default_model
        
        # Model configurations
        self.model_configs = {
            "anthropic/claude-3-sonnet": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "cost_per_1k_tokens": 0.003
            },
            "anthropic/claude-3-haiku": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "cost_per_1k_tokens": 0.00025
            },
            "openai/gpt-4-turbo": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "cost_per_1k_tokens": 0.01
            },
            "openai/gpt-3.5-turbo": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "cost_per_1k_tokens": 0.002
            },
            "meta-llama/llama-3-70b-instruct": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "cost_per_1k_tokens": 0.00059
            }
        }
    
    def get_llm(self, model: str = None) -> OpenRouterLLM:
        """Get LLM instance"""
        model = model or self.default_model
        config = self.model_configs.get(model, self.model_configs[self.default_model])
        
        return OpenRouterLLM(
            api_key=self.api_key,
            model=model,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"]
        )
    
    async def call_llm_with_tracking(self,
                                   prompt: str,
                                   model: str = None,
                                   interaction_id: str = None,
                                   prompt_mode: str = "general",
                                   **kwargs) -> Dict[str, Any]:
        """Call LLM with database tracking"""
        model = model or self.default_model
        start_time = time.time()
        
        # Prepare request data
        request_data = {
            'interaction_id': interaction_id,
            'provider': 'openrouter',
            'model': model,
            'prompt_mode': prompt_mode,
            'prompt_text': prompt,
            'request_parameters': kwargs,
            'created_at': datetime.utcnow()
        }
        
        try:
            # Get LLM instance
            llm = self.get_llm(model)
            
            # Make the call
            response_text = llm(prompt, **kwargs)
            
            # Calculate metrics
            response_time = time.time() - start_time
            tokens_used = self._estimate_tokens(prompt + response_text)
            cost = self._calculate_cost(model, tokens_used)
            
            # Update request data with response
            request_data.update({
                'response_text': response_text,
                'tokens_used': tokens_used,
                'cost_estimate': cost,
                'response_time': response_time,
                'success': True,
                'completed_at': datetime.utcnow()
            })
            
            # Save to database
            request_id = self.db_service.save_llm_request(request_data)
            
            return {
                'content': response_text,
                'tokens_used': tokens_used,
                'cost_estimate': cost,
                'response_time': response_time,
                'success': True,
                'request_id': request_id
            }
            
        except Exception as e:
            # Update request data with error
            request_data.update({
                'error_message': str(e),
                'success': False,
                'response_time': time.time() - start_time,
                'completed_at': datetime.utcnow()
            })
            
            # Save error to database
            self.db_service.save_llm_request(request_data)
            
            raise e
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3  # Rough approximation
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate cost based on model and token count"""
        config = self.model_configs.get(model, self.model_configs[self.default_model])
        return (tokens / 1000) * config["cost_per_1k_tokens"]
    
    def get_optimal_model(self, task_type: str, complexity: str = "medium") -> str:
        """Get optimal model based on task type and complexity"""
        model_recommendations = {
            "nlu_parser_failure": {
                "low": "anthropic/claude-3-haiku",
                "medium": "anthropic/claude-3-sonnet",
                "high": "openai/gpt-4-turbo"
            },
            "narrative_generation": {
                "low": "anthropic/claude-3-haiku",
                "medium": "anthropic/claude-3-sonnet",
                "high": "anthropic/claude-3-sonnet"
            },
            "dialogue_generation": {
                "low": "anthropic/claude-3-haiku",
                "medium": "anthropic/claude-3-sonnet",
                "high": "anthropic/claude-3-sonnet"
            },
            "world_query": {
                "low": "openai/gpt-3.5-turbo",
                "medium": "anthropic/claude-3-sonnet",
                "high": "openai/gpt-4-turbo"
            }
        }
        
        return model_recommendations.get(task_type, {}).get(complexity, self.default_model)