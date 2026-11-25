"""AWS Lambda: triggered by IoT Core, stores readings and sends alerts."""
import json
import os
from decimal import Decimal

import boto3

from rules import evaluate, validate

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
sns = boto3.client("sns")


def handler(event, context):
    try:
        reading = validate(event)
    except ValueError as err:
        print(f"Rejected reading {json.dumps(event)}: {err}")
        return {"stored": False, "error": str(err)}

    status, advice = evaluate(reading)
    key = {"field_id": reading["field_id"]}

    # Latest earlier reading, used to alert only when the status changes.
    previous = table.query(
        KeyConditionExpression="field_id = :f AND #t < :t",
        ExpressionAttributeNames={"#t": "timestamp"},
        ExpressionAttributeValues={":f": key["field_id"], ":t": reading["timestamp"]},
        ScanIndexForward=False,
        Limit=1,
    )["Items"]

    # DynamoDB needs Decimal instead of float.
    item = json.loads(json.dumps({**reading, "status": status}), parse_float=Decimal)
    table.put_item(Item=item)

    changed = not previous or previous[0]["status"] != status
    alerted = bool(advice) and changed
    if alerted:
        sns.publish(
            TopicArn=os.environ["TOPIC_ARN"],
            Subject=f"Farm alert: {status}",
            Message=f"Field {key['field_id']} ({reading['crop']})\n" + "\n".join(advice),
        )

    return {"stored": True, "status": status, "alerted": alerted}
