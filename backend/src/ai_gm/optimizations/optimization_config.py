"""
AI GM Performance Configuration - Centralized optimization settings

This module provides centralized configuration for all AI GM performance optimizations,
allowing fine-tuning of async processing, caching, and concurrency settings.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import os


@dataclass
class OptimizationConfig:
    """Configuration class for AI GM performance optimizations"""
    
    # Concurrency settings
    max_concurrent_reactions: int = 8
    max_concurrent_batches: int = 3
    max_concurrent_llm_calls: int = 5
    
    # Timeout settings
    reaction_timeout: float = 4.0
    llm_timeout: float = 6.0
    batch_timeout: float = 1.0
    priority_timeout: float = 2.0
    
    # Cache settings
    cache_max_size: int = 1000
    cache_default_ttl: int = 300  # 5 minutes
    cache_hit_threshold: float = 0.7  # Target cache hit rate
    
    # Batch processing settings
    batch_size: int = 5
    batch_processing_enabled: bool = True
    intelligent_batching: bool = True
    
    # Feature toggles
    enable_intelligent_fallbacks: bool = True
    enable_priority_processing: bool = True
    enable_background_updates: bool = True
    enable_performance_monitoring: bool = True
    enable_adaptive_optimization: bool = True
    
    # Quality vs Speed settings
    quality_mode: str = "balanced"  # "fast", "balanced", "quality"
    prefer_cache_over_accuracy: bool = False
    fallback_threshold: float = 0.8  # Use fallback if quality below this
    
    # Resource management
    memory_limit_mb: int = 512
    cpu_usage_threshold: float = 0.8
    enable_resource_monitoring: bool = True
    
    # Logging and monitoring
    log_level: str = "INFO"
    metrics_log_interval: int = 60  # seconds
    performance_report_interval: int = 300  # 5 minutes
    
    # Model-specific settings
    model_preferences: Dict[str, str] = field(default_factory=lambda: {
        "fast": "openai/gpt-3.5-turbo",
        "standard": "openai/gpt-4o",
        "premium": "anthropic/claude-3-opus"
    })
    
    # Advanced optimization settings
    adaptive_timeout_enabled: bool = True
    load_balancing_enabled: bool = True
    circuit_breaker_enabled: bool = True
    rate_limiting_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'max_concurrent_reactions': self.max_concurrent_reactions,
            'max_concurrent_batches': self.max_concurrent_batches,
            'max_concurrent_llm_calls': self.max_concurrent_llm_calls,
            'reaction_timeout': self.reaction_timeout,
            'llm_timeout': self.llm_timeout,
            'batch_timeout': self.batch_timeout,
            'priority_timeout': self.priority_timeout,
            'cache_max_size': self.cache_max_size,
            'cache_default_ttl': self.cache_default_ttl,
            'cache_hit_threshold': self.cache_hit_threshold,
            'batch_size': self.batch_size,
            'batch_processing_enabled': self.batch_processing_enabled,
            'intelligent_batching': self.intelligent_batching,
            'enable_intelligent_fallbacks': self.enable_intelligent_fallbacks,
            'enable_priority_processing': self.enable_priority_processing,
            'enable_background_updates': self.enable_background_updates,
            'enable_performance_monitoring': self.enable_performance_monitoring,
            'enable_adaptive_optimization': self.enable_adaptive_optimization,
            'quality_mode': self.quality_mode,
            'prefer_cache_over_accuracy': self.prefer_cache_over_accuracy,
            'fallback_threshold': self.fallback_threshold,
            'memory_limit_mb': self.memory_limit_mb,
            'cpu_usage_threshold': self.cpu_usage_threshold,
            'enable_resource_monitoring': self.enable_resource_monitoring,
            'log_level': self.log_level,
            'metrics_log_interval': self.metrics_log_interval,
            'performance_report_interval': self.performance_report_interval,
            'model_preferences': self.model_preferences,
            'adaptive_timeout_enabled': self.adaptive_timeout_enabled,
            'load_balancing_enabled': self.load_balancing_enabled,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'rate_limiting_enabled': self.rate_limiting_enabled
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OptimizationConfig':
        """Create configuration from dictionary"""
        return cls(**config_dict)
    
    @classmethod
    def from_environment(cls) -> 'OptimizationConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Load from environment with AI_GM_OPT_ prefix
        env_mappings = {
            'AI_GM_OPT_MAX_CONCURRENT_REACTIONS': ('max_concurrent_reactions', int),
            'AI_GM_OPT_REACTION_TIMEOUT': ('reaction_timeout', float),
            'AI_GM_OPT_CACHE_SIZE': ('cache_max_size', int),
            'AI_GM_OPT_CACHE_TTL': ('cache_default_ttl', int),
            'AI_GM_OPT_BATCH_SIZE': ('batch_size', int),
            'AI_GM_OPT_QUALITY_MODE': ('quality_mode', str),
            'AI_GM_OPT_LOG_LEVEL': ('log_level', str),
            'AI_GM_OPT_ENABLE_FALLBACKS': ('enable_intelligent_fallbacks', bool),
            'AI_GM_OPT_ENABLE_BACKGROUND': ('enable_background_updates', bool)
        }
        
        for env_var, (attr_name, attr_type) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    if attr_type == bool:
                        value = env_value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = attr_type(env_value)
                    setattr(config, attr_name, value)
                except (ValueError, TypeError):
                    pass  # Keep default value if conversion fails
        
        return config


# Predefined optimization profiles
OPTIMIZATION_PROFILES = {
    "development": OptimizationConfig(
        max_concurrent_reactions=3,
        reaction_timeout=6.0,
        cache_max_size=500,
        cache_default_ttl=180,
        quality_mode="fast",
        enable_performance_monitoring=True,
        log_level="DEBUG"
    ),
    
    "production_fast": OptimizationConfig(
        max_concurrent_reactions=12,
        reaction_timeout=2.0,
        cache_max_size=2000,
        cache_default_ttl=600,
        quality_mode="fast",
        prefer_cache_over_accuracy=True,
        enable_adaptive_optimization=True,
        log_level="WARNING"
    ),
    
    "production_balanced": OptimizationConfig(
        max_concurrent_reactions=8,
        reaction_timeout=4.0,
        cache_max_size=1500,
        cache_default_ttl=300,
        quality_mode="balanced",
        enable_adaptive_optimization=True,
        log_level="INFO"
    ),
    
    "production_quality": OptimizationConfig(
        max_concurrent_reactions=5,
        reaction_timeout=8.0,
        cache_max_size=1000,
        cache_default_ttl=120,
        quality_mode="quality",
        prefer_cache_over_accuracy=False,
        fallback_threshold=0.9,
        log_level="INFO"
    ),
    
    "testing": OptimizationConfig(
        max_concurrent_reactions=2,
        reaction_timeout=10.0,
        cache_max_size=100,
        cache_default_ttl=60,
        quality_mode="balanced",
        enable_performance_monitoring=True,
        enable_background_updates=False,
        log_level="DEBUG"
    )
}


class ConfigurationManager:
    """Manager for optimization configuration with runtime adjustments"""
    
    def __init__(self, profile: str = "production_balanced"):
        """
        Initialize configuration manager
        
        Args:
            profile: Optimization profile name or "auto" for automatic detection
        """
        self.profile_name = profile
        
        if profile == "auto":
            self.profile_name = self._detect_optimal_profile()
        
        self.config = self._load_configuration(self.profile_name)
        self.runtime_adjustments = {}
        
    def _detect_optimal_profile(self) -> str:
        """Automatically detect optimal configuration profile"""
        # Check if in development environment
        if os.environ.get('AI_GM_ENV') == 'development':
            return "development"
        
        # Check if in testing environment
        if os.environ.get('AI_GM_ENV') == 'testing':
            return "testing"
        
        # Check for production environment hints
        if os.environ.get('AI_GM_ENV') == 'production':
            # Check performance preference
            perf_mode = os.environ.get('AI_GM_PERFORMANCE_MODE', 'balanced')
            return f"production_{perf_mode}"
        
        # Default to balanced production
        return "production_balanced"
    
    def _load_configuration(self, profile_name: str) -> OptimizationConfig:
        """Load configuration by profile name"""
        if profile_name in OPTIMIZATION_PROFILES:
            base_config = OPTIMIZATION_PROFILES[profile_name]
        else:
            base_config = OPTIMIZATION_PROFILES["production_balanced"]
        
        # Override with environment variables
        env_config = OptimizationConfig.from_environment()
        
        # Merge configurations (environment overrides profile)
        config_dict = base_config.to_dict()
        env_dict = env_config.to_dict()
        
        # Only override non-default environment values
        default_config = OptimizationConfig()
        default_dict = default_config.to_dict()
        
        for key, value in env_dict.items():
            if value != default_dict[key]:  # Environment value differs from default
                config_dict[key] = value
        
        return OptimizationConfig.from_dict(config_dict)
    
    def get_config(self) -> OptimizationConfig:
        """Get current configuration with runtime adjustments"""
        if not self.runtime_adjustments:
            return self.config
        
        # Apply runtime adjustments
        config_dict = self.config.to_dict()
        config_dict.update(self.runtime_adjustments)
        return OptimizationConfig.from_dict(config_dict)
    
    def adjust_runtime_setting(self, setting: str, value: Any) -> bool:
        """
        Adjust a configuration setting at runtime
        
        Args:
            setting: Setting name
            value: New value
            
        Returns:
            True if adjustment was successful
        """
        try:
            # Validate setting exists
            if not hasattr(self.config, setting):
                return False
            
            # Store runtime adjustment
            self.runtime_adjustments[setting] = value
            return True
            
        except Exception:
            return False
    
    def reset_runtime_adjustments(self):
        """Reset all runtime adjustments"""
        self.runtime_adjustments.clear()
    
    def get_performance_recommendations(self, 
                                      current_metrics: Dict[str, Any]) -> List[str]:
        """
        Generate performance recommendations based on current metrics
        
        Args:
            current_metrics: Current performance metrics
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        config = self.get_config()
        
        # Analyze response times
        avg_response_time = current_metrics.get('avg_response_time', 0)
        if avg_response_time > config.reaction_timeout * 0.8:
            recommendations.append(
                "Response times approaching timeout limit. Consider increasing concurrency or timeout values."
            )
        
        # Analyze cache performance
        cache_hit_rate = current_metrics.get('cache_hit_rate', 0)
        if cache_hit_rate < config.cache_hit_threshold:
            recommendations.append(
                f"Cache hit rate ({cache_hit_rate:.1f}%) below target ({config.cache_hit_threshold:.1f}%). "
                "Consider increasing cache size or TTL."
            )
        
        # Analyze concurrency utilization
        concurrent_usage = current_metrics.get('concurrent_usage', 0)
        if concurrent_usage > 0.9:
            recommendations.append(
                "High concurrency utilization detected. Consider increasing max_concurrent_reactions."
            )
        elif concurrent_usage < 0.3:
            recommendations.append(
                "Low concurrency utilization. Consider reducing max_concurrent_reactions to save resources."
            )
        
        # Analyze fallback usage
        fallback_rate = current_metrics.get('fallback_rate', 0)
        if fallback_rate > 0.2:
            recommendations.append(
                "High fallback usage detected. Check LLM connectivity and consider increasing timeouts."
            )
        
        return recommendations
    
    def suggest_profile_change(self, current_metrics: Dict[str, Any]) -> Optional[str]:
        """
        Suggest a different optimization profile based on current performance
        
        Args:
            current_metrics: Current performance metrics
            
        Returns:
            Suggested profile name or None if current profile is optimal
        """
        avg_response_time = current_metrics.get('avg_response_time', 0)
        error_rate = current_metrics.get('error_rate', 0)
        cache_hit_rate = current_metrics.get('cache_hit_rate', 0)
        
        # If response times are too high, suggest faster profile
        if avg_response_time > 5.0 and self.profile_name != "production_fast":
            return "production_fast"
        
        # If error rate is high, suggest quality profile
        if error_rate > 0.1 and self.profile_name != "production_quality":
            return "production_quality"
        
        # If performance is excellent, suggest balanced profile
        if (avg_response_time < 2.0 and error_rate < 0.05 and cache_hit_rate > 0.8 
            and self.profile_name == "production_fast"):
            return "production_balanced"
        
        return None


# Global configuration instance
_global_config_manager = None


def get_optimization_config(profile: str = "auto") -> OptimizationConfig:
    """
    Get optimization configuration
    
    Args:
        profile: Configuration profile name
        
    Returns:
        OptimizationConfig instance
    """
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager(profile)
    
    return _global_config_manager.get_config()


def get_config_manager(profile: str = "auto") -> ConfigurationManager:
    """
    Get configuration manager instance
    
    Args:
        profile: Configuration profile name
        
    Returns:
        ConfigurationManager instance
    """
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager(profile)
    
    return _global_config_manager


def reset_global_config():
    """Reset global configuration manager"""
    global _global_config_manager
    _global_config_manager = None
