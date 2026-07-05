using System.ComponentModel.DataAnnotations.Schema;
using System.Reflection;
using HealthApp.API.Models;

namespace HealthApp.Tests.Data
{
    /// <summary>
    /// Tester för Iteration 1 av Issue #32 (DataDbContext EF mappings).
    /// Använder reflection istället för riktig DbContext-instans
    /// eftersom vi verifierar mapping-attribut och arkitekturregler,
    /// inte runtime-beteende.
    /// </summary>
    public class DataDbContextTests
    {
        // Arkitekturregel FR-003: UserData får INTE innehålla auth-fält.
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

        // FR-002: Verifiera att UserData mappar mot users-tabellen
        // och att kolumnnamn följer snake_case från schema.sql.
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

        // FR-004: EquipmentData ska mappa mot equipment-tabellen (lookup).
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

        // FR-005: ExerciseData ska ha ny kolumn calories_per_minute
        // efter Iteration 1 (kompletterar tidigare minimal mappning).
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

        // FR-006: ExerciseData ska ha navigation property till EquipmentData
        // via EquipmentId (foreign key).
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
    }
}