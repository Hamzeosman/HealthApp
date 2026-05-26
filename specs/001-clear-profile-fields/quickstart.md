# Quickstart: Clear Optional Profile Fields

## Overview

This feature enables users to clear their Goal and FitnessLevel profile fields via `PUT /api/user/me`.

**Semantics**:
- Omit field or send `null` → preserve existing value
- Send `""` (empty string) → clear the field
- Send non-empty string → update to new value

## Prerequisites

- HealthApp.API running locally (`dotnet run`)
- Valid JWT token from `/api/auth/login`
- User with Goal or FitnessLevel set

## Test the Feature

### 1. Get Current Profile

```bash
curl -X GET http://localhost:5137/api/user/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Clear Goal Field

```bash
curl -X PUT http://localhost:5137/api/user/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal": ""}'
```

**Expected**: Goal field becomes empty in response.

### 3. Clear FitnessLevel Field

```bash
curl -X PUT http://localhost:5137/api/user/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fitnessLevel": ""}'
```

**Expected**: FitnessLevel field becomes empty in response.

### 4. Verify Preservation (Omit Fields)

```bash
curl -X PUT http://localhost:5137/api/user/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"age": 25}'
```

**Expected**: Age updates, Goal and FitnessLevel remain unchanged.

## Verification Checklist

- [ ] Sending `""` for Goal clears it
- [ ] Sending `""` for FitnessLevel clears it
- [ ] Omitting Goal preserves existing value
- [ ] Omitting FitnessLevel preserves existing value
- [ ] Sending `null` preserves existing value
- [ ] Sending whitespace `"   "` clears the field
- [ ] Mixed operations work (update one, clear another, preserve third)

## Common Issues

| Issue | Solution |
|-------|----------|
| Field not clearing | Ensure you send `""` not `null` |
| 401 Unauthorized | Check JWT token is valid and included |
| Existing data lost | Verify you're omitting (not nulling) fields to preserve |
