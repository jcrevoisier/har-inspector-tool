import argparse
import sys
import json
from typing import List, Optional
from .parser import HarParser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="HAR Inspector Tool - Parse HAR files and extract API endpoints"
    )
    
    parser.add_argument(
        "har_file",
        help="Path to the HAR file to analyze"
    )
    
    parser.add_argument(
        "-d", "--domain",
        help="Filter endpoints by domain"
    )
    
    parser.add_argument(
        "-m", "--method",
        help="Filter endpoints by HTTP method (GET, POST, etc.)"
    )
    
    parser.add_argument(
        "-s", "--status",
        type=int,
        help="Filter endpoints by HTTP status code"
    )
    
    parser.add_argument(
        "-p", "--pattern",
        help="Filter endpoints by URL path pattern (regex)"
    )
    
    parser.add_argument(
        "-a", "--api-only",
        action="store_true",
        help="Only show API endpoints"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (supports .json and .csv)"
    )
    
    parser.add_argument(
        "--list-domains",
        action="store_true",
        help="List all unique domains in the HAR file"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    parsed_args = parse_args(args)
    
    try:
        parser = HarParser(parsed_args.har_file)
        
        if parsed_args.list_domains:
            domains = parser.get_unique_domains()
            print("Unique domains found:")
            for domain in sorted(domains):
                print(f"  - {domain}")
            return 0
        
        if parsed_args.api_only:
            endpoints = parser.get_api_endpoints()
        else:
            endpoints = parser.get_endpoints(
                domain=parsed_args.domain,
                method=parsed_args.method,
                status_code=parsed_args.status,
                path_pattern=parsed_args.pattern
            )
        
        if parsed_args.output:
            parser.export_endpoints(endpoints, parsed_args.output)
            print(f"Exported {len(endpoints)} endpoints to {parsed_args.output}")
        else:
            # Print to stdout
            print(json.dumps(endpoints, indent=2))
            
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
