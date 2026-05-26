# Research: Clear Optional Profile Fields

**Feature**: 001-clear-profile-fields
**Date**: 2026-05-25

## Current Implementation Analysis

### Existing Code Pattern

The current `UserService.UpdateProfileAsync` method uses `!string.IsNullOrWhiteSpace()` checks:

```csharp
if (!string.IsNullOrWhiteSpace(dto.FitnessLevel)) user.FitnessLevel = dto.FitnessLevel;
if (!string.IsNullOrWhiteSpace(dto.Goal)) user.Goal = dto.Goal;
```

**Problem**: This pattern cannot distinguish between:
- `null` (field omitted from JSON) → should preserve existing value
- `""` (empty string sent) → should clear the field
- `"   "` (whitespace only) → should clear the field

All three cases currently result in "preserve existing value" behavior.

### Technical Constraint

The `User` entity defines Goal and FitnessLevel as non-nullable strings with empty default:
```csharp
public string FitnessLevel { get; set; } = string.Empty;
public string Goal { get; set; } = string.Empty;
```

This means "cleared" state = empty string in database (not null).

## Design Decision: Explicit Clear Semantics

### Decision
Use tristate semantics in UpdateProfileDto where:
- `null` = preserve existing value (field omitted from request)
- `""` (empty string) = clear the field (set to empty in database)
- non-empty string = update to new value

### Rationale
1. **Backward compatible**: Clients sending `null` or omitting fields get same behavior as before
2. **Explicit intent**: Empty string is an explicit user action, not an accidental omission
3. **No DTO changes needed**: `string?` already allows null vs empty distinction
4. **Simple implementation**: Only service layer logic changes

### Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Sentinel value (e.g., `"__CLEAR__"`) | Explicit | Magic string, API pollution | Rejected |
| Separate clear endpoint | RESTful | Extra endpoint, more complexity | Rejected |
| Boolean flags (`ClearGoal: true`) | Explicit | DTO changes, extra fields | Rejected |
| Empty string = clear | No changes to DTO | Could be accidental | **Selected** |

## Implementation Approach

### Service Layer Change

Replace:
```csharp
if (!string.IsNullOrWhiteSpace(dto.FitnessLevel)) user.FitnessLevel = dto.FitnessLevel;
if (!string.IsNullOrWhiteSpace(dto.Goal)) user.Goal = dto.Goal;
```

With:
```csharp
// FitnessLevel: null = preserve, empty/whitespace = clear, value = update
if (dto.FitnessLevel != null)
{
    user.FitnessLevel = string.IsNullOrWhiteSpace(dto.FitnessLevel)
        ? string.Empty
        : dto.FitnessLevel;
}

// Goal: null = preserve, empty/whitespace = clear, value = update
if (dto.Goal != null)
{
    user.Goal = string.IsNullOrWhiteSpace(dto.Goal)
        ? string.Empty
        : dto.Goal;
}
```

### No DTO Changes Required

The existing `UpdateProfileDto` already supports this:
```csharp
public string? FitnessLevel { get; set; }  // nullable - can be null, empty, or value
public string? Goal { get; set; }          // nullable - can be null, empty, or value
```

### Test Cases Required

1. **Preserve**: Send `null` (omit field) → existing value unchanged
2. **Clear**: Send `""` → field becomes empty string
3. **Clear (whitespace)**: Send `"   "` → field becomes empty string (normalized)
4. **Update**: Send `"Build Muscle"` → field updated to new value
5. **Mixed**: Update Goal, clear FitnessLevel, omit Age → all three behaviors work

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing clients | Low | Medium | Null behavior unchanged |
| Accidental clears | Low | Low | Empty string requires explicit action |
| Data loss | Very Low | High | Tests verify preservation behavior |
