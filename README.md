# HAR Inspector Tool

A Python tool for parsing HAR (HTTP Archive) files and automatically extracting API endpoints.

## Features

- Parse HAR files and extract API endpoints
- Filter endpoints by domain, method, status code, etc.
- Export results to various formats (JSON, CSV, etc.)
- Command-line interface for easy integration

## Installation

```bash
pip install har-inspector-tool
```

Or install from source:

```bash
git clone https://github.com/yourusername/har-inspector-tool.git
cd har-inspector-tool
pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
har-inspector input.har

# Filter by domain
har-inspector input.har --domain api.example.com

# Filter by HTTP method
har-inspector input.har --method POST

# Export to JSON
har-inspector input.har --output endpoints.json

# Get help
har-inspector --help
```

### Python API

```python
from har_inspector import HarParser

# Parse a HAR file
parser = HarParser('input.har')

# Get all endpoints
endpoints = parser.get_endpoints()

# Filter endpoints
api_endpoints = parser.get_endpoints(
    domain='api.example.com',
    method='POST',
    status_code=200
)

# Export to file
parser.export_endpoints(endpoints, 'endpoints.json')
```

## License

MIT