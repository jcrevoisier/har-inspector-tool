import json
import csv
import re
import os
from urllib.parse import urlparse
from typing import Dict, List, Optional, Union, Set


class HarParser:
    """Parser for HAR (HTTP Archive) files to extract API endpoints."""
    
    def __init__(self, har_file_path: str):
        """
        Initialize the HAR parser with a file path.
        
        Args:
            har_file_path: Path to the HAR file
        """
        self.har_file_path = har_file_path
        self.har_data = self._load_har_file()
        
    def _load_har_file(self) -> Dict:
        """
        Load and parse the HAR file.
        
        Returns:
            Dict containing the parsed HAR data
        """
        try:
            with open(self.har_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid HAR file format: {self.har_file_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"HAR file not found: {self.har_file_path}")
    
    def get_endpoints(self, 
                     domain: Optional[str] = None,
                     method: Optional[str] = None,
                     status_code: Optional[int] = None,
                     path_pattern: Optional[str] = None) -> List[Dict]:
        """
        Extract API endpoints from the HAR file with optional filtering.
        
        Args:
            domain: Filter by domain name
            method: Filter by HTTP method (GET, POST, etc.)
            status_code: Filter by HTTP status code
            path_pattern: Filter by URL path pattern (regex)
            
        Returns:
            List of dictionaries containing endpoint information
        """
        if 'log' not in self.har_data or 'entries' not in self.har_data['log']:
            return []
        
        endpoints = []
        
        for entry in self.har_data['log']['entries']:
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            url = request.get('url', '')
            parsed_url = urlparse(url)
            
            # Skip if domain filter is provided and doesn't match
            if domain and parsed_url.netloc != domain:
                continue
                
            # Skip if method filter is provided and doesn't match
            request_method = request.get('method', '')
            if method and request_method != method:
                continue
                
            # Skip if status code filter is provided and doesn't match
            response_status = response.get('status', 0)
            if status_code and response_status != status_code:
                continue
                
            # Skip if path pattern is provided and doesn't match
            if path_pattern and not re.search(path_pattern, parsed_url.path):
                continue
                
            # Extract query parameters
            query_params = {}
            for param in request.get('queryString', []):
                query_params[param.get('name', '')] = param.get('value', '')
                
            # Extract headers
            headers = {}
            for header in request.get('headers', []):
                headers[header.get('name', '')] = header.get('value', '')
                
            # Extract post data if available
            post_data = None
            if 'postData' in request:
                post_data = request['postData'].get('text', '')
                try:
                    # Try to parse as JSON
                    post_data = json.loads(post_data)
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if not valid JSON
                    pass
            
            endpoint_info = {
                'url': url,
                'method': request_method,
                'protocol': parsed_url.scheme,
                'domain': parsed_url.netloc,
                'path': parsed_url.path,
                'query_params': query_params,
                'headers': headers,
                'post_data': post_data,
                'status_code': response_status,
                'response_size': response.get('bodySize', 0),
                'time': entry.get('time', 0),  # Response time in ms
            }
            
            endpoints.append(endpoint_info)
            
        return endpoints
    
    def get_unique_domains(self) -> Set[str]:
        """
        Extract all unique domains from the HAR file.
        
        Returns:
            Set of domain names
        """
        domains = set()
        
        if 'log' in self.har_data and 'entries' in self.har_data['log']:
            for entry in self.har_data['log']['entries']:
                request = entry.get('request', {})
                url = request.get('url', '')
                parsed_url = urlparse(url)
                domains.add(parsed_url.netloc)
                
        return domains
    
    def get_api_endpoints(self, api_patterns: List[str] = None) -> List[Dict]:
        """
        Extract likely API endpoints based on common patterns.
        
        Args:
            api_patterns: List of regex patterns to identify API endpoints
            
        Returns:
            List of dictionaries containing API endpoint information
        """
        if api_patterns is None:
            # Default patterns to identify API endpoints
            api_patterns = [
                r'/api/',
                r'/v\d+/',
                r'/rest/',
                r'/graphql',
                r'/gql',
                r'\.json$',
            ]
            
        pattern = '|'.join(api_patterns)
        return self.get_endpoints(path_pattern=pattern)
    
    def export_endpoints(self, endpoints: List[Dict], output_file: str) -> None:
        """
        Export endpoints to a file.
        
        Args:
            endpoints: List of endpoint dictionaries
            output_file: Path to the output file
        """
        file_ext = os.path.splitext(output_file)[1].lower()
        
        if file_ext == '.json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(endpoints, f, indent=2)
        elif file_ext == '.csv':
            if not endpoints:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("No endpoints found")
                return
                
            # Flatten the nested dictionaries for CSV export
            flattened = []
            for ep in endpoints:
                flat_ep = {
                    'url': ep['url'],
                    'method': ep['method'],
                    'protocol': ep['protocol'],
                    'domain': ep['domain'],
                    'path': ep['path'],
                    'status_code': ep['status_code'],
                    'response_size': ep['response_size'],
                    'time': ep['time'],
                }
                flattened.append(flat_ep)
                
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                writer.writeheader()
                writer.writerows(flattened)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
