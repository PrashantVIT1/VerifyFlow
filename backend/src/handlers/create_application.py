
import json
import uuid
import os
import boto3
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")

        full_name = body.get("full_name", "").strip()
        email = body.get("email", "").strip()
        phone = body.get("phone", "").strip()

        if not full_name or not email or not phone:
            return response(400, {
                "error": "full_name, email and phone are required"
            })

        application_id = str(uuid.uuid4())

        application = {
            "application_id": application_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "document_type": "PAN",
            "status": "PENDING_DOCUMENT_UPLOAD",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        table_name = os.environ["APPLICATIONS_TABLE"]
        table = dynamodb.Table(table_name)

        table.put_item(Item=application)

        logger.info(
            "KYC application created: %s",
            application_id
        )

        return response(201, {
            "message": "KYC application created successfully",
            "application": application
        })

    except (json.JSONDecodeError, AttributeError):
        return response(400, {
            "error": "Invalid request body"
        })

    except Exception:
        logger.exception("Failed to create KYC application")
        return response(500, {
            "error": "Unable to create KYC application"
        })


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
        },
        "body": json.dumps(body)
    }
