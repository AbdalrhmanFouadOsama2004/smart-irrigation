"""Simulate field sensors. Use --local to try it without an AWS account."""
import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FIELDS = {"field-1": "wheat", "field-2": "maize", "field-3": "tomato"}


def make_reading(field_id):
    return {
        "field_id": field_id,
        "crop": FIELDS[field_id],
        "soil_moisture": round(random.uniform(15, 90), 1),
        "temperature_c": round(random.uniform(15, 43), 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", help="no AWS, print results")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    if args.local:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from rules import evaluate, validate
    else:
        import boto3
        iot = boto3.client("iot-data")

    for round_number in range(args.rounds):
        for field_id in FIELDS:
            reading = make_reading(field_id)
            if args.local:
                status, advice = evaluate(validate(reading))
                print(f"{field_id} {reading['crop']:7} {status:12} {' '.join(advice)}")
            else:
                iot.publish(topic=f"farm/{field_id}/readings", qos=1,
                            payload=json.dumps(reading))
                print("sent", reading)
        if round_number < args.rounds - 1:
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
