"""
API documentation configuration for Aqua.
"""

from fastapi.openapi.utils import get_openapi
from typing import Dict

def custom_openapi(app) -> Dict:
    """Generate custom OpenAPI schema for documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Aqua IoT Security Scanner API",
        version="1.0.0",
        description="API documentation for Aqua IoT Security Scanner. This API allows you to perform security assessments, device discovery, and vulnerability analysis for IoT devices.",
        routes=app.routes,
    )

    # Custom documentation
    openapi_schema["info"]["x-logo"] = {
        "url": "static/img/logo.png"
    }

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
