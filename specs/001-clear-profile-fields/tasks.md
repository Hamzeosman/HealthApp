# Tasks: Clear Optional Profile Fields

**Input**: Design documents from `specs/001-clear-profile-fields/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/

**Tests**: Tests are included per constitution principle III (Test-Required).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Services**: `Services/UserService.cs`
- **Tests**: `HealthApp.Tests/Services/UserServiceTests.cs`

---

## Phase 1: Setup

**Purpose**: Verify environment and create test infrastructure

- [x] T001 Verify existing tests pass by running `dotnet test HealthApp.Tests/`
- [x] T002 Create test file structure at `HealthApp.Tests/Services/UserServiceTests.cs`

**Checkpoint**: Test infrastructure ready

---

## Phase 2: Foundational

**Purpose**: No foundational changes needed - existing infrastructure supports this feature

**Note**: This feature modifies existing service logic only. No new models, DTOs, or migrations required.

**Checkpoint**: Foundation verified - proceed to user stories

---

## Phase 3: User Story 1 - Clear Fitness Goal (Priority: P1)

**Goal**: Users can clear their Goal field by sending an empty string

**Independent Test**: Set a goal, clear it with `""`, verify Goal becomes empty

### Tests for User Story 1

- [x] T003 [P] [US1] Write test: preserve Goal when DTO.Goal is null in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T004 [P] [US1] Write test: clear Goal when DTO.Goal is empty string in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T005 [P] [US1] Write test: clear Goal when DTO.Goal is whitespace in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T006 [P] [US1] Write test: update Goal when DTO.Goal has value in `HealthApp.Tests/Services/UserServiceTests.cs`

### Implementation for User Story 1

- [x] T007 [US1] Modify Goal update logic in `Services/UserService.cs` UpdateProfileAsync method (line 32)

**Checkpoint**: User Story 1 complete - Goal clearing works independently

---

## Phase 4: User Story 2 - Clear Fitness Level (Priority: P1)

**Goal**: Users can clear their FitnessLevel field by sending an empty string

**Independent Test**: Set a fitness level, clear it with `""`, verify FitnessLevel becomes empty

### Tests for User Story 2

- [x] T008 [P] [US2] Write test: preserve FitnessLevel when DTO.FitnessLevel is null in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T009 [P] [US2] Write test: clear FitnessLevel when DTO.FitnessLevel is empty string in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T010 [P] [US2] Write test: update FitnessLevel when DTO.FitnessLevel has value in `HealthApp.Tests/Services/UserServiceTests.cs`

### Implementation for User Story 2

- [x] T011 [US2] Modify FitnessLevel update logic in `Services/UserService.cs` UpdateProfileAsync method (line 31)

**Checkpoint**: User Story 2 complete - FitnessLevel clearing works independently

---

## Phase 5: User Story 3 - Mixed Operations (Priority: P2)

**Goal**: Users can update, clear, and preserve different fields in a single request

**Independent Test**: Send request that updates Goal, clears FitnessLevel, and omits Age

### Tests for User Story 3

- [x] T012 [P] [US3] Write test: mixed operation - update Goal + clear FitnessLevel in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T013 [P] [US3] Write test: mixed operation - clear Goal + update FitnessLevel in `HealthApp.Tests/Services/UserServiceTests.cs`
- [x] T014 [P] [US3] Write test: clear already-empty field succeeds silently in `HealthApp.Tests/Services/UserServiceTests.cs`

**Checkpoint**: User Story 3 complete - mixed operations work correctly

---

## Phase 6: Polish & Verification

**Purpose**: Final verification and cleanup

- [x] T015 Run all tests to verify no regressions: `dotnet test HealthApp.Tests/`
- [x] T016 Manual verification using quickstart.md test scenarios
- [x] T017 Update spec.md status from "Draft" to "Implemented"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - verify only
- **User Story 1 (Phase 3)**: Depends on Setup completion
- **User Story 2 (Phase 4)**: Depends on Setup completion (can run parallel with US1)
- **User Story 3 (Phase 5)**: Depends on US1 and US2 completion (tests combined behavior)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - tests and implements Goal clearing
- **User Story 2 (P1)**: Independent - tests and implements FitnessLevel clearing
- **User Story 3 (P2)**: Depends on US1 + US2 (tests combined behavior)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation makes tests pass
- Story complete when all tests green

### Parallel Opportunities

- T003, T004, T005, T006 can run in parallel (different test methods)
- T008, T009, T010 can run in parallel (different test methods)
- T012, T013, T014 can run in parallel (different test methods)
- US1 and US2 can be implemented in parallel (different lines in same file)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 tests in parallel:
Task: "Write test: preserve Goal when null"
Task: "Write test: clear Goal when empty"
Task: "Write test: clear Goal when whitespace"
Task: "Write test: update Goal when has value"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Skip Phase 2: Foundational (no changes needed)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run tests, verify Goal clearing works
5. Ready for demo/review

### Full Implementation

1. Setup (Phase 1)
2. User Story 1 (Phase 3) → Test independently
3. User Story 2 (Phase 4) → Test independently (can parallel with US1)
4. User Story 3 (Phase 5) → Test combined behavior
5. Polish (Phase 6) → Final verification

### Parallel Team Strategy

With 2 developers:
- Developer A: User Story 1 (Goal clearing)
- Developer B: User Story 2 (FitnessLevel clearing)
- Together: User Story 3 (mixed operations)

---

## Notes

- Single file modification: `Services/UserService.cs` lines 31-32
- All tests in single file: `HealthApp.Tests/Services/UserServiceTests.cs`
- No schema changes, no migrations, no DTO changes
- Backward compatible: null behavior unchanged
- Total code change: ~8 lines of production code
