using HealthApp.API.DTOs;
using HealthApp.API.Models;
using HealthApp.API.Repositories;
using HealthApp.API.Services;
using HealthApp.Tests.Builders;
using Moq;

namespace HealthApp.Tests.Services
{
    public class UserServiceTests
    {
        private readonly Mock<IUserRepository> _userRepositoryMock;
        private readonly UserService _sut;

        public UserServiceTests()
        {
            _userRepositoryMock = new Mock<IUserRepository>();
            _sut = new UserService(_userRepositoryMock.Object);
        }

        private void GivenUser(User user) =>
            _userRepositoryMock.Setup(r => r.GetByIdAsync(user.Id)).ReturnsAsync(user);

        private void GivenNoUser() =>
            _userRepositoryMock.Setup(r => r.GetByIdAsync(It.IsAny<int>())).ReturnsAsync((User?)null);

        [Fact]
        public async Task GetProfileAsync_WhenUserExists_ReturnsProfileDto()
        {
            var user = new UserBuilder()
                .WithId(42).WithName("alice").WithEmail("alice@example.com")
                .WithAge(30).WithWeight(65.5m).WithHeight(170)
                .WithFitnessLevel("Intermediate").WithGoal("Run a marathon")
                .Build();
            GivenUser(user);

            var result = await _sut.GetProfileAsync(user.Id);

            Assert.NotNull(result);
            Assert.Equal(user.Name, result.Name);
            Assert.Equal(user.Email, result.Email);
            Assert.Equal(user.Age, result.Age);
            Assert.Equal(user.WeightKg, result.WeightKg);
            Assert.Equal(user.HeightCm, result.HeightCm);
            Assert.Equal(user.FitnessLevel, result.FitnessLevel);
            Assert.Equal(user.Goal, result.Goal);
        }

        [Fact]
        public async Task GetProfileAsync_WhenUserNotFound_ReturnsNull()
        {
            GivenNoUser();

            var result = await _sut.GetProfileAsync(999);

            Assert.Null(result);
        }

        [Fact]
        public async Task GetProfileAsync_DoesNotExposePasswordHash()
        {
            const string secret = "SECRET-HASH";
            var user = new UserBuilder().WithPasswordHash(secret).Build();
            GivenUser(user);

            var result = await _sut.GetProfileAsync(user.Id);

            Assert.NotNull(result);
            Assert.DoesNotContain(secret, System.Text.Json.JsonSerializer.Serialize(result));
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenUserExists_PersistsChangesAndReturnsUpdatedDto()
        {
            var user = new UserBuilder().WithAge(25).WithWeight(60).Build();
            GivenUser(user);

            var dto = new UpdateProfileDto
            {
                Age = 26,
                WeightKg = 62.3m,
                HeightCm = 168,
                FitnessLevel = "Advanced",
                Goal = "Powerlift"
            };

            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            Assert.NotNull(result);
            Assert.Equal(dto.Age, result.Age);
            Assert.Equal(dto.WeightKg, result.WeightKg);
            Assert.Equal(dto.HeightCm, result.HeightCm);
            Assert.Equal(dto.FitnessLevel, result.FitnessLevel);
            Assert.Equal(dto.Goal, result.Goal);

            Assert.Equal(dto.Age, user.Age);
            Assert.Equal(dto.WeightKg, user.WeightKg);

            _userRepositoryMock.Verify(r => r.SaveChangesAsync(), Times.Once);
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenUserNotFound_ReturnsNullAndDoesNotSave()
        {
            GivenNoUser();

            var result = await _sut.UpdateProfileAsync(999, new UpdateProfileDto());

            Assert.Null(result);
            _userRepositoryMock.Verify(r => r.SaveChangesAsync(), Times.Never);
        }

        #region Partial Update Coverage (regression tests for PR #23)

        [Fact]
        public async Task UpdateProfileAsync_WithPartialDto_OnlyUpdatesProvidedFields()
        {
            // Arrange: user har befintliga värden i alla fält
            var user = new UserBuilder()
                .WithAge(30)
                .WithWeight(75m)
                .WithHeight(180m)
                .WithFitnessLevel("Intermediate")
                .WithGoal("Bygga muskler")
                .Build();
            GivenUser(user);

            // Act: bara Goal skickas in (partial update)
            var dto = new UpdateProfileDto { Goal = "Gå ner i vikt" };
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal uppdaterad, övriga fält bevarade
            Assert.NotNull(result);
            Assert.Equal("Gå ner i vikt", result.Goal);
            Assert.Equal(30, result.Age);                      // bevarad
            Assert.Equal(75m, result.WeightKg);                // bevarad
            Assert.Equal(180m, result.HeightCm);               // bevarad
            Assert.Equal("Intermediate", result.FitnessLevel); // bevarad
        }

        [Fact]
        public async Task UpdateProfileAsync_WithNullAge_PreservesExistingAge()
        {
            // Arrange: user har ålder satt
            var user = new UserBuilder().WithAge(35).Build();
            GivenUser(user);

            // Act: skicka in dto med Age = null (men annat fält satt)
            var dto = new UpdateProfileDto { Age = null, Goal = "Annat mål" };
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: ålder ska INTE raderas av null
            Assert.NotNull(result);
            Assert.Equal(35, result.Age);
            Assert.Equal(35, user.Age);
        }

        [Fact]
        public async Task UpdateProfileAsync_WithOnlyGoal_DoesNotTouchWeightOrHeight()
        {
            // Arrange: user har vikt och längd
            var user = new UserBuilder()
                .WithWeight(80m)
                .WithHeight(175m)
                .Build();
            GivenUser(user);

            // Act: skicka in dto där bara Goal är satt
            var dto = new UpdateProfileDto { Goal = "Nytt mål" };
            await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: vikt och längd ska vara orörda på entiteten
            Assert.Equal(80m, user.WeightKg);
            Assert.Equal(175m, user.HeightCm);
        }

        [Fact]
        public async Task UpdateProfileAsync_WithEmptyDto_StillSavesChanges()
        {
            // Arrange: user finns med befintlig ålder
            var user = new UserBuilder().WithAge(40).Build();
            GivenUser(user);

            // Act: skicka in helt tom dto
            var dto = new UpdateProfileDto();
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: ingen krash, befintlig data bevaras, SaveChangesAsync anropas ändå
            // (designval — befintlig impl sparar även om inget ändrats)
            Assert.NotNull(result);
            Assert.Equal(40, result.Age);
            _userRepositoryMock.Verify(r => r.SaveChangesAsync(), Times.Once);
        }

        #endregion

        #region US1: Clear Goal Tests

        [Fact]
        public async Task UpdateProfileAsync_WhenGoalIsNull_PreservesExistingGoal()
        {
            // Arrange: User has existing goal
            var user = new UserBuilder().WithGoal("Lose Weight").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { Goal = null };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal unchanged
            Assert.NotNull(result);
            Assert.Equal("Lose Weight", result.Goal);
            Assert.Equal("Lose Weight", user.Goal);
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenGoalIsEmptyString_ClearsGoal()
        {
            // Arrange: User has existing goal
            var user = new UserBuilder().WithGoal("Build Muscle").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { Goal = "" };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal cleared to empty string
            Assert.NotNull(result);
            Assert.Equal(string.Empty, result.Goal);
            Assert.Equal(string.Empty, user.Goal);
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenGoalIsWhitespace_ClearsGoal()
        {
            // Arrange: User has existing goal
            var user = new UserBuilder().WithGoal("Maintain Fitness").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { Goal = "   " };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal cleared (whitespace normalized to empty)
            Assert.NotNull(result);
            Assert.Equal(string.Empty, result.Goal);
            Assert.Equal(string.Empty, user.Goal);
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenGoalHasValue_UpdatesGoal()
        {
            // Arrange: User has existing goal
            var user = new UserBuilder().WithGoal("Old Goal").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { Goal = "New Goal" };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal updated to new value
            Assert.NotNull(result);
            Assert.Equal("New Goal", result.Goal);
            Assert.Equal("New Goal", user.Goal);
        }

        #endregion

        #region US2: Clear FitnessLevel Tests

        [Fact]
        public async Task UpdateProfileAsync_WhenFitnessLevelIsNull_PreservesExistingFitnessLevel()
        {
            // Arrange: User has existing fitness level
            var user = new UserBuilder().WithFitnessLevel("Intermediate").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { FitnessLevel = null };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: FitnessLevel unchanged
            Assert.NotNull(result);
            Assert.Equal("Intermediate", result.FitnessLevel);
            Assert.Equal("Intermediate", user.FitnessLevel);
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenFitnessLevelIsEmptyString_ClearsFitnessLevel()
        {
            // Arrange: User has existing fitness level
            var user = new UserBuilder().WithFitnessLevel("Beginner").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { FitnessLevel = "" };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: FitnessLevel cleared to empty string
            Assert.NotNull(result);
            Assert.Equal(string.Empty, result.FitnessLevel);
            Assert.Equal(string.Empty, user.FitnessLevel);
        }

        [Fact]
        public async Task UpdateProfileAsync_WhenFitnessLevelHasValue_UpdatesFitnessLevel()
        {
            // Arrange: User has existing fitness level
            var user = new UserBuilder().WithFitnessLevel("Beginner").Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { FitnessLevel = "Advanced" };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: FitnessLevel updated to new value
            Assert.NotNull(result);
            Assert.Equal("Advanced", result.FitnessLevel);
            Assert.Equal("Advanced", user.FitnessLevel);
        }

        #endregion

        #region US3: Mixed Operations Tests

        [Fact]
        public async Task UpdateProfileAsync_MixedOperation_UpdateGoalAndClearFitnessLevel()
        {
            // Arrange: User has both fields set
            var user = new UserBuilder()
                .WithGoal("Lose Weight")
                .WithFitnessLevel("Beginner")
                .Build();
            GivenUser(user);

            var dto = new UpdateProfileDto
            {
                Goal = "Build Muscle",
                FitnessLevel = ""
            };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal updated, FitnessLevel cleared
            Assert.NotNull(result);
            Assert.Equal("Build Muscle", result.Goal);
            Assert.Equal(string.Empty, result.FitnessLevel);
        }

        [Fact]
        public async Task UpdateProfileAsync_MixedOperation_ClearGoalAndUpdateFitnessLevel()
        {
            // Arrange: User has both fields set
            var user = new UserBuilder()
                .WithGoal("Build Muscle")
                .WithFitnessLevel("Beginner")
                .Build();
            GivenUser(user);

            var dto = new UpdateProfileDto
            {
                Goal = "",
                FitnessLevel = "Intermediate"
            };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Goal cleared, FitnessLevel updated
            Assert.NotNull(result);
            Assert.Equal(string.Empty, result.Goal);
            Assert.Equal("Intermediate", result.FitnessLevel);
        }

        [Fact]
        public async Task UpdateProfileAsync_ClearAlreadyEmptyField_SucceedsSilently()
        {
            // Arrange: User has no goal set (empty string)
            var user = new UserBuilder().WithGoal(string.Empty).Build();
            GivenUser(user);

            var dto = new UpdateProfileDto { Goal = "" };

            // Act
            var result = await _sut.UpdateProfileAsync(user.Id, dto);

            // Assert: Operation succeeds, Goal remains empty
            Assert.NotNull(result);
            Assert.Equal(string.Empty, result.Goal);
            _userRepositoryMock.Verify(r => r.SaveChangesAsync(), Times.Once);
        }

        #endregion
    }
}