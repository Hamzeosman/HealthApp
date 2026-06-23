<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0 (minor amendment)
Modified principles: None
Added sections:
  - Development Workflow → "PR Size Discipline" sub-section
  - Technology Constraints → "Architecture" sub-section (data boundary)
Removed sections: N/A
Rationale: Codify two team agreements that emerged from PR #26 retrospective:
  - PR size limits to keep reviews tractable and high-quality
  - Clear ownership boundary between .NET AppDbContext and Python API
Templates requiring updates: None (sub-sections, not new principles)
Follow-up TODOs: None
-->

# HealthApp API Constitution

## Core Principles

### I. Layered Architecture

All features MUST follow the established layered architecture pattern:
- **Controllers**: Handle HTTP requests/responses, input validation, authentication
- **Services**: Contain business logic, orchestrate operations
- **Repositories**: Data access layer, EF Core interactions
- **Models/DTOs**: Data structures separated by concern (domain vs transfer)

Rationale: Clear separation enables independent testing, maintainability, and team
scalability. Direct database access from controllers is prohibited.

### II. Security-First

All endpoints MUST enforce appropriate security measures:
- Authentication via JWT Bearer tokens for protected resources
- Input validation on all user-provided data (DTOs, query parameters)
- Password hashing via BCrypt (never store plaintext)
- Follow OWASP Top 10 guidelines for web API security
- Sensitive data MUST NOT appear in logs or error responses

Rationale: Health data is sensitive. Security vulnerabilities expose user privacy
and create legal liability.

### III. Test-Required

Tests MUST accompany all new features and bug fixes:
- Unit tests for services and business logic
- Integration tests for API endpoints and database operations
- Tests can be written alongside implementation (not strictly TDD)
- All tests MUST pass before merging to master

Rationale: HealthApp handles user health data where bugs have real consequences.
Test coverage prevents regressions and validates correctness.

### IV. RESTful API Standards

All API endpoints MUST follow REST conventions:
- Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Return consistent response formats and HTTP status codes
- Use plural nouns for resource collections (`/api/exercises`, not `/api/exercise`)
- Document endpoints via OpenAPI/Scalar
- Version breaking changes appropriately

Rationale: Consistent API design enables frontend/mobile integration and third-party
consumption. The Python data pipeline depends on predictable API contracts.

### V. Code Quality

All code MUST meet quality standards:
- Follow C# naming conventions and .NET coding guidelines
- Use nullable reference types (enabled project-wide)
- Async/await for all I/O operations
- Repository pattern for data access
- DTOs for API boundaries (never expose domain entities directly)
- Keep methods focused and under 50 lines where practical

Rationale: Clean code reduces bugs, speeds onboarding, and enables confident
refactoring. Technical debt compounds over time.

## Technology Constraints

**Stack Requirements**:
- Runtime: .NET 10
- Framework: ASP.NET Core Web API
- ORM: Entity Framework Core with PostgreSQL (Npgsql)
- Authentication: JWT Bearer (Microsoft.AspNetCore.Authentication.JwtBearer)
- Password Hashing: BCrypt.Net-Next
- API Documentation: Scalar (OpenAPI)

**Database**:
- PostgreSQL managed by data engineering team via Python pipelines
- Migrations MUST be applied via `dotnet ef database update`
- Schema changes MUST be coordinated with data team

**Architecture (data boundary)**:
The team maintains a clear ownership boundary between the .NET API and the Python
data platform to avoid duplicated schema understanding:

- **`AppDbContext` (.NET)** → auth, identity, user profiles, and user-owned data
- **`DataDbContext` (.NET)** → EF mappings for shared analytics tables that .NET
  reads directly (workout sessions, exercises, equipment, etc.)
- **Python API** → analytics, AI coach, readiness scores, model predictions
- **.NET aggregates** Python API responses when the frontend needs combined data

New tables in the Python data platform MUST be classified as either EF-mapped
(consumed via `DataDbContext`) or API-only (consumed via Python API) before the
.NET integration begins. This decision is documented in the relevant GitHub issue.

Rationale: Mapping all Python tables into EF would duplicate schema knowledge
and create churn whenever the data team iterates internally. API-first for
analytics keeps the data team's autonomy and reduces coupling.

**Testing**:
- Test project: HealthApp.Tests
- Framework: xUnit (recommended) or NUnit
- Mocking: Moq or NSubstitute

## Development Workflow

**Branch Strategy**:
- `master` is the protected main branch
- Feature branches: `feature/description` or `[ticket]-description`
- Fix branches: `fix/description`
- All changes require pull request review

**Code Review Requirements**:
- At least one approval required before merge
- All CI checks must pass (build, tests, linting)
- Security-sensitive changes require additional scrutiny

**PR Size Discipline**:
Pull requests MUST be sized so that a teammate can review them meaningfully in
roughly 30 minutes. Concretely:

- Target ≤ 400 changed lines per PR (excluding lockfiles and generated files)
- One logical change per PR (a feature, a refactor, a migration — not all three)
- Larger work MUST be split into a sequence of focused PRs

If a PR exceeds the size target it MUST be justified in the PR description, OR
split before review begins. PR authors are responsible for keeping reviewers'
time tractable.

Rationale: Large PRs degrade review quality — reviewers either skim or block,
both of which hurt the codebase. Smaller PRs merge faster, are easier to revert,
and give junior contributors realistic chances to participate in review.

**Commit Standards**:
- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
- Reference issue/ticket numbers where applicable
- Keep commits atomic and focused

## Governance

This constitution supersedes conflicting practices. All development work MUST
comply with these principles.

**Amendment Process**:
1. Propose changes via pull request to constitution
2. Document rationale for changes
3. Obtain team consensus
4. Update version according to semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle or section added
   - PATCH: Clarifications, typo fixes, non-semantic updates

**Compliance**:
- All PRs should verify adherence to principles
- Violations MUST be justified in PR description with rationale
- Use CLAUDE.md for runtime development guidance and context

**Version**: 1.1.0 | **Ratified**: 2026-05-25 | **Last Amended**: 2026-05-27