from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from collections import Counter

from ..shared.models import Character, DomainType


class ShadowProfile:
    """Shadow profile that tracks a character's domain usage patterns over time"""
    
    def __init__(self, character_id: str):
        self.character_id = character_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Core domain usage counters
        self.domain_usage: Dict[DomainType, int] = {}
        for domain_type in DomainType:
            self.domain_usage[domain_type] = 0
        
        # Time-based tracking (recent vs. overall)
        self.recent_actions: List[dict] = []  # Last 20 actions
        self.recent_period_days = 7  # Track "recent" as last 7 days
        
        # Domain usage by time period (days, weeks, months)
        self.daily_usage: Dict[str, Dict[DomainType, int]] = {}
        self.weekly_usage: Dict[str, Dict[DomainType, int]] = {}
        self.monthly_usage: Dict[str, Dict[DomainType, int]] = {}
        
        # Preference tracking
        self.domain_preferences: Dict[str, float] = {}
    
    def log_domain_use(self, domain: DomainType, action: str, amount: int = 1):
        """Log domain usage
        
        Args:
            domain: The domain being used
            action: Description of the action
            amount: Weight of the usage (default 1)
        """
        # Update counters
        if domain in self.domain_usage:
            self.domain_usage[domain] += amount
        else:
            self.domain_usage[domain] = amount
        
        # Record timestamp and action
        timestamp = datetime.now()
        action_record = {
            "domain": domain,
            "action": action,
            "amount": amount,
            "timestamp": timestamp
        }
        
        # Add to recent actions, keeping only the last 20
        self.recent_actions.append(action_record)
        if len(self.recent_actions) > 20:
            self.recent_actions.pop(0)
        
        # Update time-based tracking
        self._update_time_tracking(domain, amount, timestamp)
        
        # Update domain preferences
        self._update_preferences()
        
        # Update timestamp
        self.updated_at = timestamp
    
    def _update_time_tracking(self, domain: DomainType, amount: int, timestamp: datetime):
        """Update time-based tracking buckets"""
        # Format keys for time periods
        day_key = timestamp.strftime("%Y-%m-%d")
        week_key = f"{timestamp.year}-W{timestamp.isocalendar()[1]}"
        month_key = timestamp.strftime("%Y-%m")
        
        # Update daily tracking
        if day_key not in self.daily_usage:
            self.daily_usage[day_key] = {d: 0 for d in DomainType}
        self.daily_usage[day_key][domain] += amount
        
        # Update weekly tracking
        if week_key not in self.weekly_usage:
            self.weekly_usage[week_key] = {d: 0 for d in DomainType}
        self.weekly_usage[week_key][domain] += amount
        
        # Update monthly tracking
        if month_key not in self.monthly_usage:
            self.monthly_usage[month_key] = {d: 0 for d in DomainType}
        self.monthly_usage[month_key][domain] += amount
        
        # Clean up old tracking data (keep last 90 days)
        cutoff_date = timestamp - timedelta(days=90)
        for key in list(self.daily_usage.keys()):
            try:
                day_date = datetime.strptime(key, "%Y-%m-%d")
                if day_date < cutoff_date:
                    del self.daily_usage[key]
            except ValueError:
                continue
    
    def _update_preferences(self):
        """Update domain preferences based on usage patterns"""
        # Total all domain usage
        total_usage = sum(self.domain_usage.values())
        if total_usage == 0:
            return
        
        # Calculate preferences as percentages
        for domain in DomainType:
            domain_str = domain.value
            usage = self.domain_usage[domain]
            self.domain_preferences[domain_str] = (usage / total_usage) * 100
    
    def get_dominant_domains(self, limit: int = 3) -> List[Tuple[DomainType, int]]:
        """Get the most used domains
        
        Args:
            limit: Number of domains to return (default 3)
            
        Returns:
            List of (domain, usage_count) tuples, sorted by usage
        """
        sorted_domains = sorted(
            [(domain, count) for domain, count in self.domain_usage.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_domains[:limit]
    
    def get_recent_trend(self, days: int = 7) -> Dict[DomainType, int]:
        """Get the domain usage trend for recent days
        
        Args:
            days: Number of days to analyze (default 7)
            
        Returns:
            Dictionary of domains and their usage counts over the period
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_counts = {d: 0 for d in DomainType}
        
        for action in self.recent_actions:
            if action["timestamp"] >= cutoff_date:
                recent_counts[action["domain"]] += action["amount"]
        
        return recent_counts
    
    def get_personality_profile(self) -> dict:
        """Generate a personality profile based on domain usage
        
        Returns:
            Dictionary with personality traits and their strengths
        """
        # Get dominant domains
        dominant = self.get_dominant_domains(3)
        
        # Trait mappings based on domains
        traits = {
            DomainType.BODY: ["Physical", "Active", "Enduring"],
            DomainType.MIND: ["Analytical", "Studious", "Logical"],
            DomainType.SPIRIT: ["Intuitive", "Willful", "Faithful"],
            DomainType.SOCIAL: ["Charismatic", "Persuasive", "Diplomatic"],
            DomainType.CRAFT: ["Practical", "Creative", "Skilled"],
            DomainType.AUTHORITY: ["Commanding", "Strategic", "Decisive"],
            DomainType.AWARENESS: ["Perceptive", "Alert", "Cautious"]
        }
        
        # Calculate personality profile
        profile = {}
        for domain, count in dominant:
            domain_traits = traits[domain]
            strength = min(count / 10, 1.0)  # Cap at 1.0
            for trait in domain_traits:
                profile[trait] = strength
        
        return profile