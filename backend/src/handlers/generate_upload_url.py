
import json
import os
import uuid
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    region_name="ap-south-1",
    config=Config(s3={"addressing_style": "virtual"})
)

ALLOWED_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png"
}


def lambda_handler(event, context):
    try:
        path_parameters = event.get("pathParameters") or {}
        application_id = path_parameters.get("application_id")

        body = json.loads(event.get("body") or "{}")

        file_name = body.get("file_name", "").strip()
        content_type = body.get("content_type", "").strip()

        if not application_id or not file_name or not content_type:
            return response(400, {
                "error": "application_id, file_name and content_type are required"
            })

        safe_file_name = file_name.replace("\\", "/").split("/")[-1]
        extension = os.path.splitext(safe_file_name)[1].lower()

        if extension not in ALLOWED_TYPES:
            return response(400, {
                "error": "Unsupported file type. Use PDF, JPG or PNG."
            })

        if content_type != ALLOWED_TYPES[extension]:
            return response(400, {
                "error": "File extension and content type do not match."
            })

        bucket_name = os.environ["PAN_DOCUMENTS_BUCKET"]

        object_key = (
            f"applications/{application_id}/"
            f"{uuid.uuid4()}{extension}"
        )

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_key,
                "ContentType": content_type
            },
            ExpiresIn=300
        )

        return response(200, {
            "message": "Upload URL generated successfully",
            "upload_url": upload_url,
            "object_key": object_key,
            "expires_in": 300,
            "required_headers": {
                "Content-Type": content_type
            }
        })

    except (json.JSONDecodeError, AttributeError):
        return response(400, {
            "error": "Invalid request body"
        })

    except Exception:
        return response(500, {
            "error": "Unable to generate upload URL"
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
