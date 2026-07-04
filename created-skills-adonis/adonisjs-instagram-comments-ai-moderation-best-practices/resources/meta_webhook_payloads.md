# Meta Webhook Payload Examples

## 1. Instagram Comment Payload Example
This payload is delivered when a user comments on an Instagram Media (post/reel). The webhook subscription is configured for the `instagram` object, with the `comments` field.

```json
{
  "object": "instagram",
  "entry": [
    {
      "id": "17841401111111111",
      "time": 1719324000,
      "changes": [
        {
          "field": "comments",
          "value": {
            "id": "17999999999999999",
            "text": "This product is amazing! I highly recommend it.",
            "from": {
              "id": "17841402222222222",
              "username": "happy_customer"
            },
            "media": {
              "id": "17899999999999999",
              "media_product_type": "FEED"
            }
          }
        }
      ]
    }
  ]
}
```

## 2. Facebook Page Comment Payload Example
This payload is delivered when a user comments on a Facebook Page post. The webhook subscription is configured for the `page` object, with the `feed` field.

```json
{
  "object": "page",
  "entry": [
    {
      "id": "10222222222222222",
      "time": 1719324000,
      "changes": [
        {
          "field": "feed",
          "value": {
            "item": "comment",
            "comment_id": "10222222222222222_10333333333333333",
            "post_id": "10222222222222222_10444444444444444",
            "parent_id": "10222222222222222_10444444444444444",
            "verb": "add",
            "message": "Is this service available in Brazil?",
            "from": {
              "id": "10555555555555555",
              "name": "João Silva"
            },
            "created_time": 1719324000
          }
        }
      ]
    }
  ]
}
```
