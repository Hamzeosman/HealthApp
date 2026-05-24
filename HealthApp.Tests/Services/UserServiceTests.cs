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
    }
}
