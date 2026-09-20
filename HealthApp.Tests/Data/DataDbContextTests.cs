using System.ComponentModel.DataAnnotations.Schema;
using System.Reflection;
using Mintakt.API.Models;

namespace HealthApp.Tests.Data
{
    /// <summary>
    /// Tester för DataDbContext EF mappings (Issue #32).
    /// Iteration 1: UserData, EquipmentData, ExerciseData-komplettering.
    /// Iteration 2: WorkoutSessionData-komplettering, WorkoutExerciseData, PersonalRecordData.
    ///
    /// Använder reflection istället för riktig DbContext-instans
    /// eftersom vi verifierar mapping-attribut och navigation properties,
    /// inte runtime-beteende.
    /// </summary>
    public class DataDbContextTests
    {
        // ── Iteration 1 ─────────────────────────────────────────────────

        // Arkitekturregel FR-003 (Iter 1): UserData får INTE innehålla auth-fält.
        // Skyddar mot att någon råkar lägga till Email/Password i framtiden.
        [Fact]
        public void UserData_MustNotHaveAuthFields()
        {
            // Arrange
            var forbiddenFields = new[] { "Email", "Password", "PasswordHash" };
            var userDataType = typeof(UserData);

            // Act
            var propertyNames = userDataType
                .GetProperties(BindingFlags.Public | BindingFlags.Instance)
                .Select(p => p.Name)
                .ToArray();

            // Assert
            foreach (var forbidden in forbiddenFields)
            {
                Assert.DoesNotContain(forbidden, propertyNames);
            }
        }

        // Iter 1 FR-002: UserData mappar mot users med snake_case-kolumner.
        [Fact]
        public void UserData_MapsToUsersTable_WithSnakeCaseColumns()
        {
            // Arrange
            var userDataType = typeof(UserData);

            // Act
            var tableAttribute = userDataType.GetCustomAttribute<TableAttribute>();
            var weightKgColumn = userDataType.GetProperty(nameof(UserData.WeightKg))
                ?.GetCustomAttribute<ColumnAttribute>();
            var fitnessLevelColumn = userDataType.GetProperty(nameof(UserData.FitnessLevel))
                ?.GetCustomAttribute<ColumnAttribute>();

            // Assert
            Assert.Equal("users", tableAttribute?.Name);
            Assert.Equal("weight_kg", weightKgColumn?.Name);
            Assert.Equal("fitness_level", fitnessLevelColumn?.Name);
        }

        // Iter 1 FR-004: EquipmentData mappar mot equipment.
        [Fact]
        public void EquipmentData_MapsToEquipmentTable()
        {
            // Arrange
            var equipmentDataType = typeof(EquipmentData);

            // Act
            var tableAttribute = equipmentDataType.GetCustomAttribute<TableAttribute>();
            var nameColumn = equipmentDataType.GetProperty(nameof(EquipmentData.Name))
                ?.GetCustomAttribute<ColumnAttribute>();

            // Assert
            Assert.Equal("equipment", tableAttribute?.Name);
            Assert.Equal("name", nameColumn?.Name);
        }

        // Iter 1 FR-005: ExerciseData har calories_per_minute (tillagd i Iter 1).
        [Fact]
        public void ExerciseData_HasCaloriesPerMinuteColumn()
        {
            // Arrange
            var exerciseDataType = typeof(ExerciseData);

            // Act
            var caloriesProperty = exerciseDataType.GetProperty(nameof(ExerciseData.CaloriesPerMinute));
            var columnAttribute = caloriesProperty?.GetCustomAttribute<ColumnAttribute>();

            // Assert
            Assert.NotNull(caloriesProperty);
            Assert.Equal(typeof(decimal?), caloriesProperty.PropertyType);
            Assert.Equal("calories_per_minute", columnAttribute?.Name);
        }

        // Iter 1 FR-006: ExerciseData har navigation till EquipmentData via EquipmentId.
        [Fact]
        public void ExerciseData_HasEquipmentNavigationProperty()
        {
            // Arrange
            var exerciseDataType = typeof(ExerciseData);

            // Act
            var equipmentNavigation = exerciseDataType.GetProperty(nameof(ExerciseData.Equipment));
            var foreignKeyAttribute = equipmentNavigation?.GetCustomAttribute<ForeignKeyAttribute>();

            // Assert
            Assert.NotNull(equipmentNavigation);
            Assert.Equal(typeof(EquipmentData), equipmentNavigation.PropertyType);
            Assert.Equal(nameof(ExerciseData.EquipmentId), foreignKeyAttribute?.Name);
        }

        // ── Iteration 2 ─────────────────────────────────────────────────

        // Iter 2 FR-001: WorkoutExerciseData mappar mot workout_exercises med snake_case-kolumner.
        [Fact]
        public void WorkoutExerciseData_MapsToWorkoutExercisesTable()
        {
            // Arrange
            var workoutExerciseType = typeof(WorkoutExerciseData);

            // Act
            var tableAttribute = workoutExerciseType.GetCustomAttribute<TableAttribute>();
            var sessionIdColumn = workoutExerciseType.GetProperty(nameof(WorkoutExerciseData.SessionId))
                ?.GetCustomAttribute<ColumnAttribute>();
            var weightKgColumn = workoutExerciseType.GetProperty(nameof(WorkoutExerciseData.WeightKg))
                ?.GetCustomAttribute<ColumnAttribute>();

            // Assert
            Assert.Equal("workout_exercises", tableAttribute?.Name);
            Assert.Equal("session_id", sessionIdColumn?.Name);
            Assert.Equal("weight_kg", weightKgColumn?.Name);
        }

        // Iter 2 FR-003: WorkoutExerciseData har navigation till Session och Exercise.
        [Fact]
        public void WorkoutExerciseData_HasSessionAndExerciseNavigations()
        {
            // Arrange
            var workoutExerciseType = typeof(WorkoutExerciseData);

            // Act
            var sessionNavigation = workoutExerciseType.GetProperty(nameof(WorkoutExerciseData.Session));
            var exerciseNavigation = workoutExerciseType.GetProperty(nameof(WorkoutExerciseData.Exercise));
            var sessionFk = sessionNavigation?.GetCustomAttribute<ForeignKeyAttribute>();
            var exerciseFk = exerciseNavigation?.GetCustomAttribute<ForeignKeyAttribute>();

            // Assert
            Assert.NotNull(sessionNavigation);
            Assert.Equal(typeof(WorkoutSessionData), sessionNavigation.PropertyType);
            Assert.Equal(nameof(WorkoutExerciseData.SessionId), sessionFk?.Name);

            Assert.NotNull(exerciseNavigation);
            Assert.Equal(typeof(ExerciseData), exerciseNavigation.PropertyType);
            Assert.Equal(nameof(WorkoutExerciseData.ExerciseId), exerciseFk?.Name);
        }

        // Iter 2 FR-004: PersonalRecordData mappar mot personal_records med snake_case-kolumner.
        [Fact]
        public void PersonalRecordData_MapsToPersonalRecordsTable()
        {
            // Arrange
            var personalRecordType = typeof(PersonalRecordData);

            // Act
            var tableAttribute = personalRecordType.GetCustomAttribute<TableAttribute>();
            var userIdColumn = personalRecordType.GetProperty(nameof(PersonalRecordData.UserId))
                ?.GetCustomAttribute<ColumnAttribute>();
            var exerciseIdColumn = personalRecordType.GetProperty(nameof(PersonalRecordData.ExerciseId))
                ?.GetCustomAttribute<ColumnAttribute>();

            // Assert
            Assert.Equal("personal_records", tableAttribute?.Name);
            Assert.Equal("user_id", userIdColumn?.Name);
            Assert.Equal("exercise_id", exerciseIdColumn?.Name);
        }

        // Iter 2 FR-005: PersonalRecordData har navigation till User och Exercise.
        [Fact]
        public void PersonalRecordData_HasUserAndExerciseNavigations()
        {
            // Arrange
            var personalRecordType = typeof(PersonalRecordData);

            // Act
            var userNavigation = personalRecordType.GetProperty(nameof(PersonalRecordData.User));
            var exerciseNavigation = personalRecordType.GetProperty(nameof(PersonalRecordData.Exercise));
            var userFk = userNavigation?.GetCustomAttribute<ForeignKeyAttribute>();
            var exerciseFk = exerciseNavigation?.GetCustomAttribute<ForeignKeyAttribute>();

            // Assert
            Assert.NotNull(userNavigation);
            Assert.Equal(typeof(UserData), userNavigation.PropertyType);
            Assert.Equal(nameof(PersonalRecordData.UserId), userFk?.Name);

            Assert.NotNull(exerciseNavigation);
            Assert.Equal(typeof(ExerciseData), exerciseNavigation.PropertyType);
            Assert.Equal(nameof(PersonalRecordData.ExerciseId), exerciseFk?.Name);
        }

        // Iter 2 FR-006: WorkoutSessionData har start_time och end_time (tillagda i Iter 2).
        [Fact]
        public void WorkoutSessionData_HasStartTimeAndEndTimeColumns()
        {
            // Arrange
            var workoutSessionType = typeof(WorkoutSessionData);

            // Act
            var startTimeProperty = workoutSessionType.GetProperty(nameof(WorkoutSessionData.StartTime));
            var endTimeProperty = workoutSessionType.GetProperty(nameof(WorkoutSessionData.EndTime));
            var startTimeColumn = startTimeProperty?.GetCustomAttribute<ColumnAttribute>();
            var endTimeColumn = endTimeProperty?.GetCustomAttribute<ColumnAttribute>();

            // Assert
            Assert.NotNull(startTimeProperty);
            Assert.Equal(typeof(DateTime?), startTimeProperty.PropertyType);
            Assert.Equal("start_time", startTimeColumn?.Name);

            Assert.NotNull(endTimeProperty);
            Assert.Equal(typeof(DateTime?), endTimeProperty.PropertyType);
            Assert.Equal("end_time", endTimeColumn?.Name);
        }

        // Iter 2 FR-007: WorkoutSessionData har navigation till User och samling WorkoutExercises.
        [Fact]
        public void WorkoutSessionData_HasUserAndWorkoutExercisesNavigations()
        {
            // Arrange
            var workoutSessionType = typeof(WorkoutSessionData);

            // Act
            var userNavigation = workoutSessionType.GetProperty(nameof(WorkoutSessionData.User));
            var userFk = userNavigation?.GetCustomAttribute<ForeignKeyAttribute>();
            var workoutExercisesNavigation = workoutSessionType.GetProperty(nameof(WorkoutSessionData.WorkoutExercises));

            // Assert
            Assert.NotNull(userNavigation);
            Assert.Equal(typeof(UserData), userNavigation.PropertyType);
            Assert.Equal(nameof(WorkoutSessionData.UserId), userFk?.Name);

            Assert.NotNull(workoutExercisesNavigation);
            Assert.Equal(typeof(ICollection<WorkoutExerciseData>), workoutExercisesNavigation.PropertyType);
        }
    }
}