# Data Model: Clear Optional Profile Fields

**Feature**: 001-clear-profile-fields
**Date**: 2026-05-25

## Affected Entities

### User (No Changes)

The User entity remains unchanged. Goal and FitnessLevel are already non-nullable strings:

| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| Id | int | No | - | Primary key |
| Name | string | No | "" | Required |
| Email | string | No | "" | Required |
| PasswordHash | string | No | "" | Required |
| Age | int? | Yes | null | Optional |
| WeightKg | decimal? | Yes | null | Optional |
| HeightCm | decimal? | Yes | null | Optional |
| **FitnessLevel** | string | No | "" | **In scope** - empty = cleared |
| **Goal** | string | No | "" | **In scope** - empty = cleared |
| CreatedAt | DateTime | No | UtcNow | Auto-set |

### UpdateProfileDto (No Changes)

The DTO already supports the required semantics:

| Field | Type | Validation | Semantics |
|-------|------|------------|-----------|
| Age | int? | Range(1, 120) | null=preserve, value=update |
| WeightKg | decimal? | Range(20, 500) | null=preserve, value=update |
| HeightCm | decimal? | Range(50, 250) | null=preserve, value=update |
| **FitnessLevel** | string? | StringLength(50) | null=preserve, ""=clear, value=update |
| **Goal** | string? | StringLength(100) | null=preserve, ""=clear, value=update |

### UserProfileDto (No Changes)

Response DTO remains unchanged:

| Field | Type | Notes |
|-------|------|-------|
| Name | string | From User |
| Email | string | From User |
| Age | int? | From User |
| WeightKg | decimal? | From User |
| HeightCm | decimal? | From User |
| FitnessLevel | string | Empty string when cleared |
| Goal | string | Empty string when cleared |
| CreatedAt | DateTime | From User |

## State Transitions

### Goal Field States

```
┌─────────────┐    Set value    ┌─────────────┐
│   Unset     │ ──────────────> │    Set      │
│ (empty "")  │                 │ ("Lose...")  │
└─────────────┘                 └─────────────┘
       ▲                               │
       │         Clear (send "")       │
       └───────────────────────────────┘
                      │
                      │  Update (send new value)
                      ▼
               ┌─────────────┐
               │    Set      │
               │("Build...")  │
               └─────────────┘
```

### Request Semantics

| JSON Payload | Goal in DTO | Resulting Action |
|--------------|-------------|------------------|
| `{}` | null | Preserve existing |
| `{"goal": null}` | null | Preserve existing |
| `{"goal": ""}` | "" | Clear to empty |
| `{"goal": "  "}` | "  " | Clear to empty (normalized) |
| `{"goal": "Build Muscle"}` | "Build Muscle" | Update to value |

## Validation Rules

No new validation rules. Existing rules apply:
- FitnessLevel: max 50 characters
- Goal: max 100 characters
- Empty string passes validation (length 0 < max)

## Database Impact

- No schema changes required
- No migrations needed
- Existing empty string values are valid "cleared" state
