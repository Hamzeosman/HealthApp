# API Contract: Profile Update

**Endpoint**: `PUT /api/user/me`
**Authentication**: Required (JWT Bearer)

## Request

### Headers

| Header | Required | Value |
|--------|----------|-------|
| Authorization | Yes | Bearer {token} |
| Content-Type | Yes | application/json |

### Body Schema

```json
{
  "age": number | null,
  "weightKg": number | null,
  "heightCm": number | null,
  "fitnessLevel": string | null,
  "goal": string | null
}
```

### Field Semantics (Goal, FitnessLevel)

| Value | Meaning | Example |
|-------|---------|---------|
| Field omitted | Preserve existing value | `{}` |
| `null` | Preserve existing value | `{"goal": null}` |
| `""` (empty string) | Clear the field | `{"goal": ""}` |
| Whitespace only | Clear the field | `{"goal": "   "}` |
| Non-empty string | Update to value | `{"goal": "Build Muscle"}` |

### Validation Rules

| Field | Rule |
|-------|------|
| age | 1-120 (if provided) |
| weightKg | 20-500 (if provided) |
| heightCm | 50-250 (if provided) |
| fitnessLevel | Max 50 characters |
| goal | Max 100 characters |

## Response

### Success (200 OK)

```json
{
  "name": "string",
  "email": "string",
  "age": number | null,
  "weightKg": number | null,
  "heightCm": number | null,
  "fitnessLevel": "string",
  "goal": "string",
  "createdAt": "2026-05-25T10:30:00Z"
}
```

**Note**: `fitnessLevel` and `goal` return empty string `""` when cleared.

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 400 Bad Request | Validation failed | `{ "errors": { "field": ["message"] } }` |
| 401 Unauthorized | Missing/invalid token | - |
| 404 Not Found | User not found | - |

## Examples

### Clear Goal Only

Request:
```json
{
  "goal": ""
}
```

Response (200):
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "weightKg": 75.5,
  "heightCm": 180.0,
  "fitnessLevel": "Intermediate",
  "goal": "",
  "createdAt": "2026-01-15T08:00:00Z"
}
```

### Update Goal, Clear FitnessLevel

Request:
```json
{
  "goal": "Build Muscle",
  "fitnessLevel": ""
}
```

Response (200):
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "weightKg": 75.5,
  "heightCm": 180.0,
  "fitnessLevel": "",
  "goal": "Build Muscle",
  "createdAt": "2026-01-15T08:00:00Z"
}
```

### Preserve All (Empty Request)

Request:
```json
{}
```

Response (200): All fields unchanged from current state.
