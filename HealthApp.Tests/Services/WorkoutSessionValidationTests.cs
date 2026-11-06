using System.ComponentModel.DataAnnotations;
using Mintakt.API.DTOs;
using Mintakt.API.Models;
using Mintakt.API.Repositories;
using Mintakt.API.Services;
using Moq;
using Xunit;

namespace HealthApp.Tests.Services
{
    /// <summary>
    /// Säkerställer att valideringen matchar CHECK-constraints i workout_sessions och
    /// workout_exercises, så att ogiltiga värden ger 400 i stället för databasfel och 500.
    /// </summary>
    public class WorkoutSessionValidationTests
    {
        private static bool IsValid(object dto)
        {
            var results = new List<ValidationResult>();
            return Validator.TryValidateObject(dto, new ValidationContext(dto), results, validateAllProperties: true);
        }

        private static CreateWorkoutExerciseDto ValidExercise() => new()
        {
            ExerciseId = 1,
            Sets = 3,
            Reps = 10,
            WeightKg = 50m,
            Rpe = 7
        };

        [Theory]
        [InlineData("bra")]
        [InlineData("okej")]
        [InlineData("trött")]
        [InlineData("stark")]
        [InlineData("")]
        [InlineData(null)]
        public void Session_WithAllowedMood_IsValid(string? mood)
        {
            // Arrange
            var dto = new CreateWorkoutSessionDto { Mood = mood };

            // Act & Assert
            Assert.True(IsValid(dto));
        }

        [Theory]
        [InlineData("glad")]
        [InlineData("BRA")]
        [InlineData("bra ")]
        public void Session_WithMoodOutsideList_IsInvalid(string mood)
        {
            // Arrange
            var dto = new CreateWorkoutSessionDto { Mood = mood };

            // Act & Assert
            Assert.False(IsValid(dto));
        }

        [Fact]
        public void Exercise_WithValidValues_IsValid()
        {
            Assert.True(IsValid(ValidExercise()));
        }

        [Theory]
        [InlineData(0)]
        [InlineData(21)]
        public void Exercise_WithSetsOutsideRange_IsInvalid(int sets)
        {
            var dto = ValidExercise();
            dto.Sets = sets;

            Assert.False(IsValid(dto));
        }

        [Theory]
        [InlineData(0)]
        [InlineData(101)]
        public void Exercise_WithRepsOutsideRange_IsInvalid(int reps)
        {
            var dto = ValidExercise();
            dto.Reps = reps;

            Assert.False(IsValid(dto));
        }

        [Theory]
        [InlineData(-1)]
        [InlineData(501)]
        public void Exercise_WithWeightOutsideRange_IsInvalid(int weightKg)
        {
            var dto = ValidExercise();
            dto.WeightKg = weightKg;

            Assert.False(IsValid(dto));
        }

        [Theory]
        [InlineData(0)]
        [InlineData(11)]
        public void Exercise_WithRpeOutsideRange_IsInvalid(int rpe)
        {
            var dto = ValidExercise();
            dto.Rpe = rpe;

            Assert.False(IsValid(dto));
        }

        [Fact]
        public void Exercise_WithoutExerciseId_IsInvalid()
        {
            var dto = ValidExercise();
            dto.ExerciseId = 0;

            Assert.False(IsValid(dto));
        }

        [Theory]
        [InlineData("")]
        [InlineData("   ")]
        [InlineData(null)]
        public async Task AddWorkoutSessionAsync_WithoutMood_SavesNull(string? mood)
        {
            // Arrange — CHECK-constrainten tillåter NULL men inte en tom sträng
            var repositoryMock = new Mock<IWorkoutSessionRepository>();
            WorkoutSessionData? saved = null;
            repositoryMock
                .Setup(r => r.AddAsync(It.IsAny<WorkoutSessionData>()))
                .Callback<WorkoutSessionData>(session => saved = session)
                .Returns(Task.CompletedTask);
            var sut = new WorkoutSessionService(repositoryMock.Object);

            // Act
            await sut.AddWorkoutSessionAsync(new CreateWorkoutSessionDto { UserId = 1, Date = DateTime.Today, Mood = mood });

            // Assert
            Assert.NotNull(saved);
            Assert.Null(saved.Mood);
        }
    }
}
