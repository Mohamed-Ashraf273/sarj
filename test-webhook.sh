#!/bin/bash

MESSAGE="${1:-Hello, is anyone there?}"
FROM="201004538215"
WEBHOOK_URL="https://sarj-ws5b.onrender.com/webhook"

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
echo "Note: Bot reply was sent to WhatsApp API for number $FROM"
echo "Check Render logs for the actual bot reply content."
