# Feature Specification: Clear Optional Profile Fields

**Feature Branch**: `001-clear-profile-fields`
**Created**: 2026-05-25
**Status**: Implemented
**Input**: User description: "Implement support for clearing optional user profile fields"

## Clarifications

### Session 2026-05-25

- Q: What should happen if a user tries to clear a field that doesn't support clearing (e.g., required fields)? → A: Scope limited to Goal/FitnessLevel; other fields use existing validation unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clear Fitness Goal (Priority: P1)

A user who previously set a fitness goal wants to remove it because their circumstances changed (injury, lifestyle change, or they simply no longer want to track against a specific goal).

**Why this priority**: Core feature request - users currently have no way to undo a goal once set, which feels like being "locked in" to a choice.

**Independent Test**: Can be fully tested by setting a goal, then clearing it, and verifying the profile no longer shows a goal.

**Acceptance Scenarios**:

1. **Given** a user with Goal set to "Lose Weight", **When** the user updates their profile with an empty Goal value, **Then** the Goal field becomes unset (cleared) in their profile.
2. **Given** a user with Goal set to "Build Muscle", **When** the user updates their profile without including the Goal field, **Then** the existing Goal value remains unchanged ("Build Muscle").
3. **Given** a user with no Goal set, **When** the user updates their profile with an empty Goal value, **Then** the profile update succeeds with no changes to Goal.

---

### User Story 2 - Clear Fitness Level (Priority: P1)

A user who previously set their fitness level wants to remove it because they prefer not to categorize themselves or their situation changed.

**Why this priority**: Same importance as clearing Goal - both fields share the same behavior pattern and user need.

**Independent Test**: Can be fully tested by setting a fitness level, then clearing it, and verifying the profile no longer shows a fitness level.

**Acceptance Scenarios**:

1. **Given** a user with FitnessLevel set to "Intermediate", **When** the user updates their profile with an empty FitnessLevel value, **Then** the FitnessLevel field becomes unset (cleared) in their profile.
2. **Given** a user with FitnessLevel set to "Beginner", **When** the user updates their profile without including the FitnessLevel field, **Then** the existing FitnessLevel value remains unchanged ("Beginner").

---

### User Story 3 - Update Profile with Mixed Operations (Priority: P2)

A user wants to update multiple profile fields in a single request, where some fields are being set to new values, some are being cleared, and some are being preserved.

**Why this priority**: Ensures the feature works correctly in realistic usage patterns where users update multiple fields at once.

**Independent Test**: Can be tested by sending a profile update that sets one field, clears another, and omits a third.

**Acceptance Scenarios**:

1. **Given** a user with Goal="Lose Weight" and FitnessLevel="Beginner", **When** the user updates their profile setting Goal to "Build Muscle", clearing FitnessLevel (empty value), **Then** Goal becomes "Build Muscle" and FitnessLevel becomes unset.
2. **Given** a user with Goal="Lose Weight" and FitnessLevel="Beginner", **When** the user updates their profile omitting Goal and setting FitnessLevel to "Intermediate", **Then** Goal remains "Lose Weight" and FitnessLevel becomes "Intermediate".

---

### Edge Cases

- What happens when a user sends an empty value for a field that is already cleared? (Should succeed silently)
- What happens when whitespace-only values are sent? (Should be treated as empty/clear intent)
- How does the system distinguish between "field not included in request" vs "field explicitly set to empty"?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to clear their Goal field by submitting an empty value
- **FR-002**: System MUST allow users to clear their FitnessLevel field by submitting an empty value
- **FR-003**: System MUST preserve existing field values when the field is not included in an update request
- **FR-004**: System MUST distinguish between "preserve existing value" (field omitted) and "clear the value" (empty value submitted)
- **FR-005**: System MUST treat whitespace-only values as clear requests (normalize to empty)
- **FR-006**: System MUST return the updated profile state after successful modification

### Key Entities

- **User Profile**: Contains optional Goal and FitnessLevel fields that can be set, updated, or cleared
- **Goal**: A string describing the user's fitness objective (e.g., "Lose Weight", "Build Muscle", "Maintain Fitness")
- **FitnessLevel**: A string describing the user's self-assessed fitness level (e.g., "Beginner", "Intermediate", "Advanced")

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully clear a previously set Goal field in a single profile update operation
- **SC-002**: Users can successfully clear a previously set FitnessLevel field in a single profile update operation
- **SC-003**: Existing profile data remains unchanged when fields are omitted from an update request (100% preservation rate)
- **SC-004**: Profile updates complete within 2 seconds under normal conditions
- **SC-005**: Zero accidental data loss incidents from the clear-field functionality (tracked via support tickets)

## Assumptions

- Users are authenticated before accessing profile update functionality (existing behavior)
- The profile update endpoint already exists and handles authentication/authorization
- Only Goal and FitnessLevel are in scope for this feature; other profile fields retain their existing validation behavior unchanged
- The existing null-bug fix (PR #23) correctly prevents accidental data loss when fields are omitted
- Client applications will be updated to understand the semantics (empty = clear, omit = preserve)
- Whitespace-only values should be normalized to empty and treated as clear requests
