
import json
import os
import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    try:
        path_parameters = event.get("pathParameters") or {}
        application_id = path_parameters.get("application_id")

        body = json.loads(event.get("body") or "{}")
        object_key = body.get("object_key", "").strip()

        if not application_id or not object_key:
            return response(400, {
                "error": "application_id and object_key are required"
            })

        # Ensure the object belongs to this application
        if not object_key.startswith(f"applications/{application_id}/"):
            return response(400, {
                "error": "Invalid document reference"
            })

        bucket_name = os.environ["PAN_DOCUMENTS_BUCKET"]

        # Check whether the document exists in S3
        document = s3.head_object(
            Bucket=bucket_name,
            Key=object_key
        )

        table = dynamodb.Table(
            os.environ["APPLICATIONS_TABLE"]
        )

        # Update the application record
        table.update_item(
            Key={"application_id": application_id},
            UpdateExpression=(
                "SET document_key = :document_key, "
                "#status = :status"
            ),
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":document_key": object_key,
                ":status": "DOCUMENT_UPLOADED"
            },
            ConditionExpression="attribute_exists(application_id)"
        )

        return response(200, {
            "message": "Document upload confirmed",
            "application_id": application_id,
            "document_key": object_key,
            "document_size": document.get("ContentLength"),
            "status": "DOCUMENT_UPLOADED"
        })

    except s3.exceptions.ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")

        if error_code in ("404", "NoSuchKey", "NotFound"):
            return response(404, {
                "error": "Uploaded document not found in S3"
            })

        return response(500, {
            "error": "Unable to verify uploaded document"
        })

    except (json.JSONDecodeError, AttributeError):
        return response(400, {
            "error": "Invalid request body"
        })

    except Exception:
        return response(500, {
            "error": "Unable to confirm document upload"
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
