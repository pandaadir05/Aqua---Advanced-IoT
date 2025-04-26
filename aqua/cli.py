#!/usr/bin/env python3
"""
Aqua IoT Security Platform CLI
Command line interface for Aqua
"""

import os
import sys
import argparse
import uvicorn

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Aqua IoT Security Platform")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Web command
    web_parser = subparsers.add_parser("web", help="Run the web interface")
    web_parser.add_argument("--port", type=int, default=8000, help="Port to run the web interface on")
    web_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    web_parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    
    args = parser.parse_args()
    
    if args.command == "web":
        # Add the project root to the Python path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, base_dir)
        
        print("Starting Aqua IoT Security Platform web interface...")
        try:
            # Make sure demo user is created (normally done in app.py)
            from aqua.web.auth import create_demo_user
            create_demo_user()
            
            # Run the web server
            uvicorn.run(
                "aqua.web.app:app",
                host=args.host,
                port=args.port,
                reload=args.reload
            )
        except ImportError as e:
            print(f"Error starting web interface: {e}")
    else:
        parser.print_help()

# This is what's expected in the __init__.py file
app = main

if __name__ == "__main__":
    main()