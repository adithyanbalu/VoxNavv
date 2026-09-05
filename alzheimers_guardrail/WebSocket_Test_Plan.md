# WebSocket Connection Test Plan

## 1. Unit Tests for WebSocket Endpoint

### 1.1 Test validate_and_sanitize function
- Test each action type with valid inputs
- Test each action type with missing required fields
- Test each action type with invalid field types
- Test invalid action type
- Test missing action field
- Test non-dictionary target

### 1.2 Test WebSocket connection acceptance
- Simulate a client connecting to the WebSocket endpoint
- Verify that the connection is accepted without errors

### 1.3 Test response structure
- For each valid action, verify that the response contains:
  - risk_result (from calculate_risk)
  - explanation (from context_result)
  - privacy_log (from context_result)

## 2. Integration Test Scenarios for All Four Action Types

### 2.1 SEND_DOCUMENT
- Valid inputs: recipient (string), document_id (optional string)
- Expected: successful processing and response

### 2.2 DELETE_FILE
- Valid inputs: document_id (used as file_id, string)
- Expected: successful processing and response

### 2.3 CANCEL_APPT
- Valid inputs: recipient (string)
- Expected: successful processing and response

### 2.4 TRANSFER
- Valid inputs: recipient (string), amount (non-negative number)
- Expected: successful processing and response

## 3. Edge Case Testing

### 3.1 Invalid Inputs
- Send invalid JSON (e.g., malformed string)
- Send missing "action" field
- Send invalid action type (not in the four allowed)
- Send target as non-dictionary
- For each action type, send missing required fields in target
- For each action type, send fields with wrong types (e.g., recipient as number)
- For TRANSFER, send negative amount
- For TRANSFER, send non-numeric amount

### 3.2 Disconnections
- Simulate client disconnecting during message transmission
- Simulate server-side disconnection (if applicable)
- Test reconnection after disconnection

### 3.3 Other Edge Cases
- Very large payloads
- Special characters in strings (to test sanitization)
- Empty strings for required fields

## 4. Performance Verification

### 4.1 Latency Test
- For each action type, send 100 requests and measure the round-trip time
- Calculate average, median, 95th percentile latency
- Verify that 95th percentile latency is under 500ms

### 4.2 Load Test
- Simulate multiple concurrent connections (e.g., 10 clients)
- Each client sends a mix of action types
- Measure system stability and latency under load

## Test Implementation Notes

- Use pytest and asyncio for testing
- Use the `websockets` library for client-side WebSocket connections
- Mock external dependencies (risk_engine, context_engine) if necessary for unit tests
- For integration tests, run the backend server on a test port (e.g., 8001)
- Ensure tests are isolated and clean up resources after each test

## Pass/Fail Criteria

- Unit tests: All unit tests must pass
- Integration tests: Each action type must be successfully processed and return a valid response
- Edge cases: Invalid inputs must return appropriate error responses without crashing
- Performance: 95th percentile latency for each action type must be <500ms under normal load