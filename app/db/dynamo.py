from datetime import datetime
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key

from app.config import settings


def _get_resource():
    kwargs = {"region_name": settings.AWS_REGION}
    if settings.DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def get_table():
    return _get_resource().Table(settings.DYNAMODB_TABLE_NAME)


def get_link(short_code: str) -> dict[str, Any] | None:
    table = get_table()
    resp = table.get_item(Key={"short_code": short_code})
    return resp.get("Item")


def put_link(
    short_code: str,
    original_url: str,
    user_id: str,
    created_at: str,
    expires_at: int | None,
) -> None:
    table = get_table()
    item = {
        "short_code": short_code,
        "original_url": original_url,
        "user_id": user_id,
        "created_at": created_at,
        "click_count": 0,
    }
    if expires_at is not None:
        item["expires_at"] = expires_at
    table.put_item(Item=item)


def delete_link(short_code: str) -> None:
    table = get_table()
    table.delete_item(Key={"short_code": short_code})


def query_links_by_user(user_id: str, limit: int = 20, last_evaluated_key: dict | None = None) -> tuple[list[dict], dict | None]:
    table = get_table()
    kwargs = {
        "IndexName": "user_id-index",
        "KeyConditionExpression": Key("user_id").eq(user_id),
        "Limit": limit,
        "ScanIndexForward": False,
    }
    if last_evaluated_key:
        kwargs["ExclusiveStartKey"] = last_evaluated_key
    resp = table.query(**kwargs)
    items = resp.get("Items", [])
    next_key = resp.get("LastEvaluatedKey")
    return items, next_key


def count_links_by_user(user_id: str) -> int:
    table = get_table()
    resp = table.query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        Select="COUNT",
    )
    return resp.get("Count", 0)


def increment_click_count(short_code: str) -> None:
    table = get_table()
    table.update_item(
        Key={"short_code": short_code},
        UpdateExpression="ADD click_count :inc",
        ExpressionAttributeValues={":inc": 1},
    )
