from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml

@dataclass
class ModelCapabilities:
    context_window: int
    description: str
    use_case: List[str]

class ModelSelector:
    def __init__(self, models_config: Dict):
        self.models = self._process_models(models_config)
        
    def _process_models(self, config: Dict) -> Dict[str, ModelCapabilities]:
        processed = {}
        for provider, models in config.items():
            for model_name, details in models.items():
                processed[model_name] = ModelCapabilities(
                    context_window=details['context_window'],
                    description=details.get('description', ''),
                    use_case=details.get('use_case', [])
                )
        return processed
    
    def select_model(self, task_description: str, requirements: Optional[Dict] = None) -> str:
        # Default requirements
        if requirements is None:
            requirements = {
                'min_context_window': 0,
                'priority': 'balanced'  # Options: speed, quality, balanced
            }
        
        # Task classification based on keywords
        task_keywords = {
            'code': ['code', 'programming', 'function', 'debug', 'development'],
            'vision': ['image', 'visual', 'picture', 'photo', 'diagram'],
            'math': ['math', 'calculation', 'equation', 'numerical'],
            'creative': ['creative', 'story', 'write', 'generate'],
            'analysis': ['analyze', 'summarize', 'extract', 'understand'],
            'tool_use': ['api', 'tool', 'function calling', 'integration']
        }
        
        # Score each model based on task requirements
        scores = {}
        for model_name, capabilities in self.models.items():
            score = 0
            
            # Context window check
            if capabilities.context_window >= requirements['min_context_window']:
                score += 1
            else:
                continue  # Skip if context window requirement not met
            
            # Task matching
            for task_type, keywords in task_keywords.items():
                if any(keyword in task_description.lower() for keyword in keywords):
                    if any(keyword in ' '.join(capabilities.use_case).lower() for keyword in keywords):
                        score += 2
            
            # Priority-based scoring
            if requirements['priority'] == 'speed':
                if capabilities.context_window < 10000:  # Smaller models are typically faster
                    score += 2
            elif requirements['priority'] == 'quality':
                if capabilities.context_window > 30000:  # Larger models often provide better quality
                    score += 2
            
            scores[model_name] = score
        
        # Select the model with the highest score
        if not scores:
            return "llama-3.1-70b-versatile"  # Default to most versatile model
        
        return max(scores.items(), key=lambda x: x[1])[0]

def create_model_selector(config_path: str = "config/models_config.yaml") -> ModelSelector:
    with open(config_path, 'r') as f:
        models_config = yaml.safe_load(f)
    return ModelSelector(models_config) 