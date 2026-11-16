
import json


def lambda_handler(event, context):
    """
    VerifyFlow health-check Lambda handler.

    Args:
        event: Incoming AWS Lambda event.
        context: AWS Lambda execution context.

    Returns:
        API Gateway-compatible HTTP response.
    """

    response = {
        "status": "healthy",
        "application": "VerifyFlow",
        "version": "1.0.0"
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
        },
        "body": json.dumps(response)
    }
