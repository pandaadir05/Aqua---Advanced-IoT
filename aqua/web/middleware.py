"""
Middleware for the Aqua web interface
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

class SessionDebugMiddleware(BaseHTTPMiddleware):
    """
    Middleware to debug session issues
    """
    async def dispatch(self, request: Request, call_next):
        # Print cookies for debugging
        session_cookie = request.cookies.get("session")
        print(f"[DEBUG] Request to {request.url.path} - Session cookie: {session_cookie}")
        
        # Process request as normal
        response = await call_next(request)
        
        # Check if response is setting cookies
        if "set-cookie" in response.headers:
            print(f"[DEBUG] Response setting cookies: {response.headers.get('set-cookie')}")
            
        return response
