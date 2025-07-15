import logging
import json
from typing import Dict, List, Any, Optional
import uuid
import os

from app.services.code_parser_service import code_parser
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store
from app.models.repository import RepositoryStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationService:
    """
    Service for generating documentation from code analysis.
    """
    
    def __init__(self):
        """
        Initialize the documentation service.
        """
        logger.info("Documentation service initialized")
    
    async def process_repository(self, repo_id: str, repo_path: str) -> None:
        """
        Process a repository to generate documentation.
        
        Args:
            repo_id: Repository ID
            repo_path: Path to the repository
        """
        try:
            # Update repository status
            from app.services.repository_service import repository_status
            repository_status[repo_id] = {
                "status": RepositoryStatus.PROCESSING,
                "progress": 0.2,
                "message": "Analyzing code structure..."
            }
            
            # Analyze the repository
            repo_structure = code_parser.analyze_repository(repo_path)
            
            # Update progress
            repository_status[repo_id] = {
                "status": RepositoryStatus.PROCESSING,
                "progress": 0.4,
                "message": "Extracting code chunks..."
            }
            
            # Extract chunks from all files
            all_chunks = []
            for file_structure in repo_structure['files']:
                chunks = code_parser.extract_chunks(file_structure)
                all_chunks.extend(chunks)
            
            # Update progress
            repository_status[repo_id] = {
                "status": RepositoryStatus.PROCESSING,
                "progress": 0.6,
                "message": "Generating embeddings..."
            }
            
            # Process chunks and generate embeddings
            embedding_service.process_chunks(all_chunks, repo_id)
            
            # Update progress
            repository_status[repo_id] = {
                "status": RepositoryStatus.PROCESSING,
                "progress": 0.8,
                "message": "Generating documentation..."
            }
            
            # Generate documentation
            documentation = self.generate_documentation(repo_id, repo_structure)
            
            # Save documentation to file
            docs_dir = os.path.join(repo_path, "documentation")
            os.makedirs(docs_dir, exist_ok=True)
            
            with open(os.path.join(docs_dir, "documentation.json"), "w") as f:
                json.dump(documentation, f, indent=2)
            
            # Update status to completed
            repository_status[repo_id] = {
                "status": RepositoryStatus.COMPLETED,
                "progress": 1.0,
                "message": "Documentation generated successfully"
            }
            
            logger.info(f"Documentation generated for repository {repo_id}")
            
        except Exception as e:
            logger.error(f"Error processing repository: {str(e)}")
            # Update status to failed
            from app.services.repository_service import repository_status
            repository_status[repo_id] = {
                "status": RepositoryStatus.FAILED,
                "progress": 0.0,
                "message": f"Failed to generate documentation: {str(e)}"
            }
            raise
    
    def generate_documentation(self, repo_id: str, repo_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation for a repository.
        
        Args:
            repo_id: Repository ID
            repo_structure: Repository structure from code analysis
            
        Returns:
            Generated documentation
        """
        documentation = {
            "repository_id": repo_id,
            "modules": []
        }
        
        # Process each file as a module
        for file_structure in repo_structure['files']:
            module_doc = self._generate_module_documentation(file_structure)
            documentation["modules"].append(module_doc)
        
        return documentation
    
    def _generate_module_documentation(self, file_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation for a module (file).
        
        Args:
            file_structure: File structure from code analysis
            
        Returns:
            Module documentation
        """
        file_path = file_structure['file_path']
        module_name = os.path.basename(file_path)
        
        module_doc = {
            "name": module_name,
            "path": file_path,
            "description": self._generate_module_description(file_structure),
            "classes": [],
            "functions": []
        }
        
        # Process classes
        for class_info in file_structure.get('classes', []):
            class_doc = {
                "name": class_info['name'],
                "description": class_info.get('docstring', 'No description available.'),
                "methods": []
            }
            
            # Process methods
            for method in class_info.get('methods', []):
                method_doc = {
                    "name": method['name'],
                    "description": method.get('docstring', 'No description available.'),
                    "parameters": self._format_parameters(method.get('params', [])),
                    "returns": method.get('returns', 'None')
                }
                class_doc["methods"].append(method_doc)
            
            module_doc["classes"].append(class_doc)
        
        # Process functions
        for func in file_structure.get('functions', []):
            func_doc = {
                "name": func['name'],
                "description": func.get('docstring', 'No description available.'),
                "parameters": self._format_parameters(func.get('params', [])),
                "returns": func.get('returns', 'None')
            }
            module_doc["functions"].append(func_doc)
        
        return module_doc
    
    def _generate_module_description(self, file_structure: Dict[str, Any]) -> str:
        """
        Generate a description for a module.
        
        Args:
            file_structure: File structure from code analysis
            
        Returns:
            Module description
        """
        # In a real implementation, this would use an LLM to generate a description
        # For now, we'll just create a simple description based on the file content
        
        num_classes = len(file_structure.get('classes', []))
        num_functions = len(file_structure.get('functions', []))
        
        description = f"This module contains {num_classes} classes and {num_functions} functions."
        
        if num_classes > 0:
            class_names = [c['name'] for c in file_structure.get('classes', [])]
            description += f" Classes: {', '.join(class_names)}."
        
        if num_functions > 0:
            function_names = [f['name'] for f in file_structure.get('functions', [])]
            description += f" Functions: {', '.join(function_names)}."
        
        return description
    
    def _format_parameters(self, params: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format parameters for documentation.
        
        Args:
            params: List of parameter information
            
        Returns:
            Formatted parameters
        """
        formatted = []
        for param in params:
            param_doc = {
                "name": param['name'],
                "type": param.get('type', 'any'),
                "description": "No description available."  # In a real implementation, this would be generated by an LLM
            }
            if 'default' in param:
                param_doc['default'] = param['default']
            
            formatted.append(param_doc)
        
        return formatted

# Create a singleton instance
documentation_service = DocumentationService()