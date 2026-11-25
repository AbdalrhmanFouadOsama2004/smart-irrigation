# Smart Irrigation Monitor (AWS + Python)

Field sensors report soil moisture and temperature. AWS stores each reading
and emails the farmer when a field needs attention.

    sensor / simulator.py
            |  MQTT topic farm/<field_id>/readings
        AWS IoT Core (rule)
            |
        AWS Lambda  --->  DynamoDB (history)
            |
        Amazon SNS  --->  email alert

## Try it locally (no AWS account)

    python simulator.py --local
    python -m unittest discover tests

## Deploy

Needs an AWS account, configured credentials (`aws configure`), the AWS SAM CLI
and Python 3.13.

    sam build
    sam deploy --guided      # stack name, region, your AlertEmail

Allow SAM to create IAM roles when asked. Then **confirm the subscription**
email from AWS, or no alerts will arrive.

    pip install -r requirements.txt
    export AWS_DEFAULT_REGION=<your region>   # PowerShell: $env:AWS_DEFAULT_REGION="..."
    python simulator.py --rounds 3

Your credentials need `iot:Publish` permission. Check the results in the
DynamoDB console (table name is in the stack outputs) and in the Lambda logs:

    sam logs --stack-name <stack name>

## Clean up

    sam delete

## Notes

- An email is sent only when a field's status changes to a problem state.
- Crop thresholds in `src/rules.py` are illustrative, not agronomic advice.
- The simulator uses random values, so expect frequent status changes.
- AWS may charge for usage; delete the stack when finished.

## Ideas to extend

Control a pump through an IoT command, skip irrigation when rain is forecast,
or add a dashboard.
