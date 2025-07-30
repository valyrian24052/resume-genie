"""Prompt configuration loader and validator for AI customization engine."""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class PromptConfig:
    """Configuration for a specific prompt type."""
    system_prompt: str
    context_template: str
    model_params: Dict[str, Any]


@dataclass
class ModelParams:
    """AI model parameters."""
    model: str
    max_tokens: int
    temperature: float
    timeout: Optional[int] = None


class PromptValidator:
    """Validator for prompt configuration files."""
    
    def __init__(self, config_data: Dict[str, Any]):
        """Initialize validator with configuration data.
        
        Args:
            config_data: Loaded YAML configuration data
        """
        self.config_data = config_data
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Define valid template variables for each prompt type
        self.valid_template_variables = {
            'summary': {
                'job_context', 'content', 'experiences_summary', 'projects_summary', 
                'skills_summary', 'education_summary', 'research_summary'
            },
            'experience': {
                'job_context', 'content', 'full_context', 'target_skills'
            },
            'skills': {
                'job_context', 'content', 'target_skills', 'user_experience_level', 
                'relevant_projects'
            },
            'projects': {
                'job_context', 'content', 'target_skills', 'technical_background'
            }
        }
        
        # Define valid model parameters and their types/ranges
        self.valid_model_params = {
            'model': {'type': str, 'required': True},
            'max_tokens': {'type': int, 'required': True, 'min': 1, 'max': 4000},
            'temperature': {'type': (int, float), 'required': True, 'min': 0.0, 'max': 2.0},
            'timeout': {'type': int, 'required': False, 'min': 1, 'max': 300},
            'top_p': {'type': (int, float), 'required': False, 'min': 0.0, 'max': 1.0},
            'frequency_penalty': {'type': (int, float), 'required': False, 'min': -2.0, 'max': 2.0},
            'presence_penalty': {'type': (int, float), 'required': False, 'min': -2.0, 'max': 2.0}
        }
    
    def validate(self) -> bool:
        """Validate the prompt configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Check top-level structure
        if not isinstance(self.config_data, dict):
            self.errors.append("Configuration must be a dictionary")
            return False
        
        # Validate required sections exist
        self._validate_required_sections()
        
        # Validate prompts structure
        self._validate_prompts_structure()
        
        # Validate template variables
        self._validate_template_variables()
        
        # Validate default parameters
        self._validate_default_params()
        
        # Log validation results
        if self.errors:
            for error in self.errors:
                logger.error(f"Prompt validation error: {error}")
        
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"Prompt validation warning: {warning}")
        
        return len(self.errors) == 0
    
    def _validate_required_sections(self):
        """Validate that all required sections exist."""
        required_sections = self.config_data.get('required_sections', [])
        prompts = self.config_data.get('prompts', {})
        
        if not isinstance(prompts, dict):
            self.errors.append("'prompts' section must be a dictionary")
            return
        
        for section in required_sections:
            if section not in prompts:
                self.errors.append(f"Required prompt section '{section}' is missing")
    
    def _validate_prompts_structure(self):
        """Validate the structure of each prompt configuration."""
        prompts = self.config_data.get('prompts', {})
        required_fields = self.config_data.get('required_prompt_fields', [])
        required_model_params = self.config_data.get('required_model_params', [])
        
        for prompt_name, prompt_config in prompts.items():
            if not isinstance(prompt_config, dict):
                self.errors.append(f"Prompt '{prompt_name}' must be a dictionary")
                continue
            
            # Check required fields
            for field in required_fields:
                if field not in prompt_config:
                    self.errors.append(f"Prompt '{prompt_name}' missing required field '{field}'")
                elif field == 'system_prompt' and not prompt_config[field].strip():
                    self.errors.append(f"Prompt '{prompt_name}' has empty system_prompt")
                elif field == 'context_template' and not prompt_config[field].strip():
                    self.errors.append(f"Prompt '{prompt_name}' has empty context_template")
            
            # Validate model parameters
            model_params = prompt_config.get('model_params', {})
            if not isinstance(model_params, dict):
                self.errors.append(f"Prompt '{prompt_name}' model_params must be a dictionary")
                continue
            
            for param in required_model_params:
                if param not in model_params:
                    self.errors.append(f"Prompt '{prompt_name}' missing required model parameter '{param}'")
                elif param == 'max_tokens' and not isinstance(model_params[param], int):
                    self.errors.append(f"Prompt '{prompt_name}' max_tokens must be an integer")
                elif param == 'temperature' and not isinstance(model_params[param], (int, float)):
                    self.errors.append(f"Prompt '{prompt_name}' temperature must be a number")
                elif param == 'model' and not isinstance(model_params[param], str):
                    self.errors.append(f"Prompt '{prompt_name}' model must be a string")
            
            # Validate all model parameters with enhanced validation
            self._validate_model_parameters(prompt_name, model_params)
    
    def _validate_template_variables(self):
        """Validate template variables in context templates."""
        import re
        
        prompts = self.config_data.get('prompts', {})
        
        for prompt_name, prompt_config in prompts.items():
            if not isinstance(prompt_config, dict):
                continue
            
            context_template = prompt_config.get('context_template', '')
            if not context_template:
                continue
            
            # Extract variables from template using regex
            template_vars = set(re.findall(r'\{(\w+)\}', context_template))
            valid_vars = self.valid_template_variables.get(prompt_name, set())
            
            # Check for invalid variables
            invalid_vars = template_vars - valid_vars
            if invalid_vars:
                self.errors.append(
                    f"Prompt '{prompt_name}' context_template contains invalid variables: {', '.join(invalid_vars)}"
                )
            
            # Check for missing common variables (warnings only)
            if prompt_name in self.valid_template_variables:
                if 'job_context' not in template_vars:
                    self.warnings.append(f"Prompt '{prompt_name}' context_template missing 'job_context' variable")
                if 'content' not in template_vars:
                    self.warnings.append(f"Prompt '{prompt_name}' context_template missing 'content' variable")
    
    def _validate_model_parameters(self, prompt_name: str, model_params: Dict[str, Any]):
        """Validate model parameters for a specific prompt.
        
        Args:
            prompt_name: Name of the prompt being validated
            model_params: Model parameters to validate
        """
        for param_name, param_value in model_params.items():
            if param_name not in self.valid_model_params:
                self.warnings.append(f"Prompt '{prompt_name}' has unknown model parameter '{param_name}'")
                continue
            
            param_config = self.valid_model_params[param_name]
            
            # Check type
            expected_type = param_config['type']
            if not isinstance(param_value, expected_type):
                self.errors.append(
                    f"Prompt '{prompt_name}' parameter '{param_name}' must be of type {expected_type.__name__}"
                )
                continue
            
            # Check range constraints
            if 'min' in param_config and param_value < param_config['min']:
                self.errors.append(
                    f"Prompt '{prompt_name}' parameter '{param_name}' ({param_value}) must be >= {param_config['min']}"
                )
            
            if 'max' in param_config and param_value > param_config['max']:
                self.errors.append(
                    f"Prompt '{prompt_name}' parameter '{param_name}' ({param_value}) must be <= {param_config['max']}"
                )
        
        # Check for required parameters
        for param_name, param_config in self.valid_model_params.items():
            if param_config.get('required', False) and param_name not in model_params:
                self.errors.append(f"Prompt '{prompt_name}' missing required model parameter '{param_name}'")
    
    def _validate_default_params(self):
        """Validate default parameters structure."""
        default_params = self.config_data.get('default_params', {})
        
        if not isinstance(default_params, dict):
            self.errors.append("'default_params' must be a dictionary")
            return
        
        # Validate default parameters using the same validation as prompt parameters
        self._validate_model_parameters('default_params', default_params)


class PromptLoader:
    """Loader for AI prompt configurations."""
    
    def __init__(self, config_path: str = "config/prompts.yaml"):
        """Initialize prompt loader.
        
        Args:
            config_path: Path to the prompt configuration file
        """
        self.config_path = config_path
        self._config_data: Optional[Dict[str, Any]] = None
        self._prompts: Optional[Dict[str, PromptConfig]] = None
        self._default_params: Optional[Dict[str, Any]] = None
    
    def load(self) -> bool:
        """Load and validate prompt configuration.
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            # Check if config file exists
            if not os.path.exists(self.config_path):
                logger.error(f"Prompt configuration file not found: {self.config_path}")
                return False
            
            # Load YAML configuration
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config_data = yaml.safe_load(file)
            
            if self._config_data is None:
                logger.error("Prompt configuration file is empty or invalid")
                return False
            
            # Validate configuration
            validator = PromptValidator(self._config_data)
            if not validator.validate():
                logger.error("Prompt configuration validation failed")
                return False
            
            # Parse prompts
            self._parse_prompts()
            
            # Load default parameters
            self._default_params = self._config_data.get('default_params', {})
            
            logger.info(f"Successfully loaded prompt configuration from {self.config_path}")
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML configuration: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to load prompt configuration: {str(e)}")
            return False
    
    def _parse_prompts(self):
        """Parse prompt configurations into PromptConfig objects."""
        self._prompts = {}
        prompts_data = self._config_data.get('prompts', {})
        
        for prompt_name, prompt_data in prompts_data.items():
            try:
                prompt_config = PromptConfig(
                    system_prompt=prompt_data['system_prompt'],
                    context_template=prompt_data['context_template'],
                    model_params=prompt_data['model_params']
                )
                self._prompts[prompt_name] = prompt_config
            except KeyError as e:
                logger.error(f"Missing required field in prompt '{prompt_name}': {str(e)}")
                raise
    
    def get_prompt(self, prompt_type: str) -> Optional[PromptConfig]:
        """Get prompt configuration for a specific type.
        
        Args:
            prompt_type: Type of prompt (e.g., 'summary', 'experience', 'skills')
            
        Returns:
            PromptConfig object or None if not found
        """
        if self._prompts is None:
            logger.error("Prompts not loaded. Call load() first.")
            return None
        
        return self._prompts.get(prompt_type)
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt types.
        
        Returns:
            List of available prompt type names
        """
        if self._prompts is None:
            return []
        
        return list(self._prompts.keys())
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get default model parameters.
        
        Returns:
            Dictionary of default parameters
        """
        return self._default_params.copy() if self._default_params else {}
    
    def reload(self) -> bool:
        """Reload configuration from file.
        
        Returns:
            True if reload successful, False otherwise
        """
        self._config_data = None
        self._prompts = None
        self._default_params = None
        return self.load()
    
    def is_loaded(self) -> bool:
        """Check if configuration is loaded.
        
        Returns:
            True if configuration is loaded, False otherwise
        """
        return self._prompts is not None