"""
AWS Lambda entry point for the webhook server.
Uses serverless-wsgi to adapt API Gateway requests to the Flask app.
Set Lambda handler to: lambda_handler.lambda_handler
"""
import sys
import os

# Ensure project root is on path when running in Lambda
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from serverless_wsgi import handle_request
from src.webhook_server import app


def lambda_handler(event, context):
    """Invoked by API Gateway. Forwards the request to the Flask app."""
    return handle_request(app, event, context)
