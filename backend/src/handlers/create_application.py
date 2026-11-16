
import json
import uuid
from datetime import datetime, timezone


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")

        # Extract applicant details
        full_name = body.get("full_name", "").strip()
        email = body.get("email", "").strip()
        phone = body.get("phone", "").strip()

        # Validate required fields
        if not full_name or not email or not phone:
            return response(400, {
                "error": "full_name, email and phone are required"
            })

        # Generate unique application ID
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

        return response(201, {
            "message": "KYC application created successfully",
            "application": application
        })

    except (json.JSONDecodeError, AttributeError):
        return response(400, {
            "error": "Invalid request body"
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
