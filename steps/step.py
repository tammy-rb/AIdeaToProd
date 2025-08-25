from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Step(ABC):
    """
    Abstract base class for all workflow steps in the AI Idea to Production pipeline.
    Each step represents a distinct phase in the development process.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a step with a name and description.
        
        Args:
            name: The name of the step
            description: A description of what this step does
        """
        self.name = name
        self.description = description
        self._result: Optional[Any] = None
    
    @abstractmethod
    def execute(self, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the step with the given input data.
        
        Args:
            input_data: Optional input data from previous steps
            
        Returns:
            Dict containing the result of the step execution
            
        Raises:
            Exception: If the step execution fails
        """
        pass
    
    def get_result(self) -> Optional[Any]:
        """
        Get the result of the last execution.
        
        Returns:
            The result of the last step execution, or None if not executed
        """
        return self._result
    
    def set_result(self, result: Any) -> None:
        """
        Set the result of the step execution.
        
        Args:
            result: The result to store
        """
        self._result = result
    
    def __str__(self) -> str:
        return f"Step: {self.name} - {self.description}"
    
    def __repr__(self) -> str:
        return f"Step(name='{self.name}', description='{self.description}')"