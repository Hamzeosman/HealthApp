# Implementation Plan: Clear Optional Profile Fields

**Branch**: `001-clear-profile-fields` | **Date**: 2026-05-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-clear-profile-fields/spec.md`

## Summary

Enable users to explicitly clear Goal and FitnessLevel profile fields via `PUT /api/user/me` by implementing tristate semantics: null=preserve, empty=clear, value=update. This is a minimal service-layer change with no DTO or schema modifications.

## Technical Context

**Language/Version**: C# / .NET 10
**Primary Dependencies**: ASP.NET Core Web API, Entity Framework Core
**Storage**: PostgreSQL (via Npgsql.EntityFrameworkCore.PostgreSQL)
**Testing**: xUnit (HealthApp.Tests project)
**Target Platform**: Linux/Windows server
**Project Type**: Web API
**Performance Goals**: <2 seconds response time (existing SLA)
**Constraints**: Backward compatible with existing clients
**Scale/Scope**: Single user profile operation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Layered Architecture | ✅ Pass | Change isolated to Service layer |
| II. Security-First | ✅ Pass | Uses existing JWT auth, no new inputs |
| III. Test-Required | ✅ Pass | Unit tests planned for all scenarios |
| IV. RESTful API Standards | ✅ Pass | Same endpoint, consistent response format |
| V. Code Quality | ✅ Pass | Async pattern maintained, clear logic |

**All gates passed. No violations.**

## Project Structure

### Documentation (this feature)

```text
specs/001-clear-profile-fields/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical research and decisions
├── data-model.md        # Entity and DTO documentation
├── quickstart.md        # Testing guide
└── contracts/
    └── profile-update.md # API contract
```

### Source Code (repository root)

```text
Services/
└── UserService.cs       # UpdateProfileAsync modification (lines 31-32)

HealthApp.Tests/
└── Services/
    └── UserServiceTests.cs  # New test file for clear scenarios
```

**Structure Decision**: Single project structure. Only UserService.cs requires modification. New test file for comprehensive coverage.

## Complexity Tracking

No violations. Single-file change with isolated scope.

## Implementation Summary

### Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `Services/UserService.cs` | Update conditional logic for Goal/FitnessLevel | ~8 lines |

### Files to Create

| File | Purpose |
|------|---------|
| `HealthApp.Tests/Services/UserServiceTests.cs` | Unit tests for update scenarios |

### Key Code Change

**Current** (`Services/UserService.cs:31-32`):
```csharp
if (!string.IsNullOrWhiteSpace(dto.FitnessLevel)) user.FitnessLevel = dto.FitnessLevel;
if (!string.IsNullOrWhiteSpace(dto.Goal)) user.Goal = dto.Goal;
```

**New**:
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

## Test Scenarios

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| T1 | Preserve Goal (null) | `{"goal": null}` | Goal unchanged |
| T2 | Preserve Goal (omit) | `{}` | Goal unchanged |
| T3 | Clear Goal (empty) | `{"goal": ""}` | Goal = "" |
| T4 | Clear Goal (whitespace) | `{"goal": "  "}` | Goal = "" |
| T5 | Update Goal | `{"goal": "Build"}` | Goal = "Build" |
| T6 | Preserve FitnessLevel (null) | `{"fitnessLevel": null}` | FitnessLevel unchanged |
| T7 | Clear FitnessLevel (empty) | `{"fitnessLevel": ""}` | FitnessLevel = "" |
| T8 | Update FitnessLevel | `{"fitnessLevel": "Pro"}` | FitnessLevel = "Pro" |
| T9 | Mixed: update+clear | `{"goal": "X", "fitnessLevel": ""}` | Goal="X", FitnessLevel="" |
| T10 | Clear already empty | `{"goal": ""}` on empty Goal | Goal = "" (success) |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing clients | Null behavior unchanged (backward compatible) |
| Accidental data loss | Empty string requires explicit client action |
| Regression | Comprehensive test coverage for all scenarios |

## Next Steps

Run `/speckit-tasks` to generate the task list for implementation.
