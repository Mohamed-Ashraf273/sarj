#!/bin/bash

MESSAGE="${1:-Hello, is anyone there?}"
FROM="201004535285"
WEBHOOK_URL="http://localhost:8000/webhook"

echo "----------------------------------------"
echo "Sending message: \"$MESSAGE\""
echo "From: $FROM"
echo "To: $WEBHOOK_URL"
echo "----------------------------------------"

RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$FROM\",
            \"type\": \"text\",
            \"text\": {\"body\": \"$MESSAGE\"}
          }]
        }
      }]
    }]
  }")

echo "Webhook response: $RESPONSE"
echo "----------------------------------------"
