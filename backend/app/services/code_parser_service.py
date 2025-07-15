import ast
import os
import logging
from typing import Dict, List, Any, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeParserService:
    """
    Service for parsing and analyzing code using AST.
    Currently supports Python code analysis.
    """

    def __init__(self):
        """
        Initialize the code parser service.
        """
        pass

    def parse_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Python file and extract its structure.

        Args:
            file_path: Path to the Python file

        Returns:
            Dictionary containing the file structure
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            tree = ast.parse(content)
            visitor = PythonASTVisitor(content)
            visitor.visit(tree)

            # Filter out methods from functions list
            visitor.filter_methods_from_functions()

            return {
                'file_path': file_path,
                'imports': visitor.imports,
                'classes': visitor.classes,
                'functions': visitor.functions,
                'variables': visitor.variables
            }
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {str(e)}")
            return {
                'file_path': file_path,
                'error': str(e)
            }

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze all Python files in a repository.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary containing the repository structure
        """
        result = {
            'repo_path': repo_path,
            'files': []
        }

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_structure = self.parse_python_file(file_path)
                    result['files'].append(file_structure)

        return result

    def extract_chunks(self, file_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract semantic chunks from a file structure.

        Args:
            file_structure: Dictionary containing the file structure

        Returns:
            List of semantic chunks
        """
        chunks = []
        file_path = file_structure['file_path']

        # Add classes and their methods as chunks
        for class_info in file_structure.get('classes', []):
            # Class chunk
            class_chunk = {
                'id': f"{file_path}:class:{class_info['name']}",
                'type': 'class',
                'name': class_info['name'],
                'file_path': file_path,
                'content': class_info['content'],
                'docstring': class_info.get('docstring', ''),
                'line_range': class_info['line_range']
            }
            chunks.append(class_chunk)

            # Method chunks
            for method in class_info.get('methods', []):
                method_chunk = {
                    'id': f"{file_path}:method:{class_info['name']}.{method['name']}",
                    'type': 'method',
                    'name': method['name'],
                    'class_name': class_info['name'],
                    'file_path': file_path,
                    'content': method['content'],
                    'docstring': method.get('docstring', ''),
                    'line_range': method['line_range'],
                    'params': method.get('params', []),
                    'returns': method.get('returns', None)
                }
                chunks.append(method_chunk)

        # Add standalone functions as chunks
        for func in file_structure.get('functions', []):
            func_chunk = {
                'id': f"{file_path}:function:{func['name']}",
                'type': 'function',
                'name': func['name'],
                'file_path': file_path,
                'content': func['content'],
                'docstring': func.get('docstring', ''),
                'line_range': func['line_range'],
                'params': func.get('params', []),
                'returns': func.get('returns', None)
            }
            chunks.append(func_chunk)

        return chunks


class PythonASTVisitor(ast.NodeVisitor):
    """
    AST visitor for Python code analysis.
    """

    def __init__(self, source_code: str):
        """
        Initialize the AST visitor.

        Args:
            source_code: Source code of the file
        """
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.imports = []
        self.classes = []
        self.functions = []
        self.variables = []

    def filter_methods_from_functions(self):
        """
        Filter out methods from the functions list.
        Methods are already included in their respective classes.
        """
        # Create a set of (name, line_range) tuples for all methods
        method_signatures = set()
        for class_info in self.classes:
            for method in class_info.get('methods', []):
                method_signatures.add((method['name'], method['line_range']))

        # Filter out functions that match method signatures
        self.functions = [
            func for func in self.functions 
            if (func['name'], func['line_range']) not in method_signatures
        ]

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visit an Import node.
        """
        for name in node.names:
            self.imports.append({
                'name': name.name,
                'alias': name.asname,
                'line': node.lineno
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visit an ImportFrom node.
        """
        module = node.module
        for name in node.names:
            self.imports.append({
                'name': f"{module}.{name.name}" if module else name.name,
                'alias': name.asname,
                'line': node.lineno
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit a ClassDef node.
        """
        class_info = {
            'name': node.name,
            'line_range': (node.lineno, self._get_end_line(node)),
            'methods': [],
            'content': self._get_node_source(node)
        }

        # Extract docstring
        docstring = ast.get_docstring(node)
        if docstring:
            class_info['docstring'] = docstring

        # Extract base classes
        if node.bases:
            class_info['bases'] = [self._get_name(base) for base in node.bases]

        # Visit class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._process_function(item)
                class_info['methods'].append(method_info)

        self.classes.append(class_info)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit a FunctionDef node (standalone function).
        """
        # Process all function definitions
        # We'll filter out methods later by comparing with class methods
        func_info = self._process_function(node)
        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Visit an Assign node (variable assignment).
        """
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append({
                    'name': target.id,
                    'line': node.lineno,
                    'value': self._get_node_source(node.value)
                })
        self.generic_visit(node)

    def _process_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Process a function or method node.
        """
        func_info = {
            'name': node.name,
            'line_range': (node.lineno, self._get_end_line(node)),
            'content': self._get_node_source(node)
        }

        # Extract docstring
        docstring = ast.get_docstring(node)
        if docstring:
            func_info['docstring'] = docstring

        # Extract parameters
        func_info['params'] = self._extract_parameters(node)

        # Extract return annotation if present
        if node.returns:
            func_info['returns'] = self._get_node_source(node.returns)

        return func_info

    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """
        Extract parameters from a function definition.
        """
        params = []
        for arg in node.args.args:
            param_info = {'name': arg.arg}
            if arg.annotation:
                param_info['type'] = self._get_node_source(arg.annotation)
            params.append(param_info)

        # Handle default values
        defaults = node.args.defaults
        if defaults:
            default_offset = len(node.args.args) - len(defaults)
            for i, default in enumerate(defaults):
                params[default_offset + i]['default'] = self._get_node_source(default)

        return params

    def _get_node_source(self, node: ast.AST) -> str:
        """
        Get the source code for a node.
        """
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            start_line = node.lineno - 1  # 0-indexed
            end_line = getattr(node, 'end_lineno', node.lineno) - 1

            if hasattr(node, 'col_offset') and hasattr(node, 'end_col_offset'):
                if start_line == end_line:
                    return self.source_lines[start_line][node.col_offset:node.end_col_offset]
                else:
                    lines = [self.source_lines[start_line][node.col_offset:]]
                    lines.extend(self.source_lines[start_line+1:end_line])
                    lines.append(self.source_lines[end_line][:node.end_col_offset])
                    return '\n'.join(lines)
            else:
                return '\n'.join(self.source_lines[start_line:end_line+1])

        return ""

    def _get_end_line(self, node: ast.AST) -> int:
        """
        Get the end line number of a node.
        """
        if hasattr(node, 'end_lineno'):
            return node.end_lineno

        # If end_lineno is not available, find the maximum line number in the node's children
        max_line = node.lineno
        for child in ast.iter_child_nodes(node):
            if hasattr(child, 'lineno'):
                child_end = self._get_end_line(child)
                max_line = max(max_line, child_end)

        return max_line

    def _get_name(self, node: ast.AST) -> str:
        """
        Get the name from a node.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            return self._get_node_source(node)

# Create a singleton instance
code_parser = CodeParserService()
