#!/bin/bash
# Test script for JSON-RPC A2A endpoint
# Usage: ./test_jsonrpc_a2a.sh [base_url]

BASE_URL="${1:-https://hng13-production-76f0.up.railway.app}"
ENDPOINT="$BASE_URL/a2a/agent/codeReviewAssistant"

echo "=========================================="
echo "Testing JSON-RPC A2A Endpoint"
echo "Base URL: $BASE_URL"
echo "=========================================="

# Test 1: Empty request (should return 200 with error message)
echo -e "\n1️⃣  Test: Empty JSON request"
RESPONSE=$(curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -s -w "\n%{http_code}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
echo "$BODY" | jq '.'
echo "HTTP Status: $HTTP_CODE"

# Test 2: Unknown method
echo -e "\n2️⃣  Test: Unknown method"
RESPONSE=$(curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-001",
    "method": "unknown/method"
  }' \
  -s -w "\n%{http_code}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
echo "$BODY" | jq '.'
echo "HTTP Status: $HTTP_CODE"

# Test 3: Help method
echo -e "\n3️⃣  Test: Help method"
RESPONSE=$(curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-002",
    "method": "help"
  }' \
  -s -w "\n%{http_code}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
echo "$BODY" | jq '.'
echo "HTTP Status: $HTTP_CODE"

# Test 4: Simple message/send
echo -e "\n4️⃣  Test: Simple code review request"
RESPONSE=$(curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-003",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          { "kind": "text", "text": "Review this Python code: def add(a,b): return a+b" }
        ],
        "messageId": "msg-001"
      },
      "configuration": { "blocking": true }
    }
  }' \
  -s -w "\n%{http_code}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
echo "$BODY" | jq '.'
echo "HTTP Status: $HTTP_CODE"

# Test 5: Complex message with multiple parts
echo -e "\n5️⃣  Test: Complex multi-part message"
RESPONSE=$(curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-004",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          { "kind": "text", "text": "Find bugs in this JavaScript:" },
          { "kind": "text", "text": "function greet(name) { console.log(\"Hello \" + name.toUpperCase()); }" }
        ],
        "messageId": "msg-002",
        "metadata": {
          "language": "javascript",
          "context": "bug-detection"
        }
      },
      "configuration": {
        "blocking": true,
        "acceptedOutputModes": ["text/plain"]
      }
    }
  }' \
  -s -w "\n%{http_code}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
echo "$BODY" | jq '.'
echo "HTTP Status: $HTTP_CODE"

echo -e "\n=========================================="
echo "Tests complete!"
echo "=========================================="
