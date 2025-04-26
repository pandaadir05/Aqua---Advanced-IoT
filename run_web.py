#!/usr/bin/env python3
"""
Aqua IoT Security Platform Web Interface
Entry point script for running the web interface
"""

import os
import sys
import argparse
import uvicorn

def main():
    """Run the Aqua web interface"""
    parser = argparse.ArgumentParser(description="Aqua IoT Security Platform Web Interface")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the web interface on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    args = parser.parse_args()
    
    print("Starting Aqua IoT Security Platform web interface...")
    uvicorn.run(
        "aqua.web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    # Make sure the package is in the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
