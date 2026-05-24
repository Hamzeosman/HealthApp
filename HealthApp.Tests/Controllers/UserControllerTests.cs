using System.Security.Claims;
using HealthApp.API.Controllers;
using HealthApp.API.DTOs;
using HealthApp.API.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Moq;

namespace HealthApp.Tests.Controllers
{
    public class UserControllerTests
    {
        private readonly Mock<IUserService> _userServiceMock;
        private readonly UserController _sut;

        public UserControllerTests()
        {
            _userServiceMock = new Mock<IUserService>();
            _sut = new UserController(_userServiceMock.Object);
        }

        private void SetUserContext(string? userIdClaim)
        {
            var claims = userIdClaim != null
                ? new[] { new Claim(ClaimTypes.NameIdentifier, userIdClaim) }
                : Array.Empty<Claim>();

            var identity = new ClaimsIdentity(claims, "TestAuth");
            _sut.ControllerContext = new ControllerContext
            {
                HttpContext = new DefaultHttpContext { User = new ClaimsPrincipal(identity) }
            };
        }

        [Fact]
        public async Task GetMyProfile_WithValidUserId_ReturnsOkWithProfile()
        {
            SetUserContext("42");
            var profile = new UserProfileDto { Name = "alice", Email = "alice@example.com" };
            _userServiceMock.Setup(s => s.GetProfileAsync(42)).ReturnsAsync(profile);

            var result = await _sut.GetMyProfile();

            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsType<UserProfileDto>(ok.Value);
            Assert.Equal("alice", returned.Name);
        }

        [Fact]
        public async Task GetMyProfile_WhenProfileNotFound_ReturnsNotFound()
        {
            SetUserContext("42");
            _userServiceMock.Setup(s => s.GetProfileAsync(42))
                .ReturnsAsync((UserProfileDto?)null);

            var result = await _sut.GetMyProfile();

            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetMyProfile_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            SetUserContext(null);

            var result = await _sut.GetMyProfile();

            Assert.IsType<UnauthorizedResult>(result);
            _userServiceMock.Verify(s => s.GetProfileAsync(It.IsAny<int>()), Times.Never);
        }

        [Fact]
        public async Task UpdateMyProfile_WithValidData_ReturnsOk()
        {
            SetUserContext("7");
            var dto = new UpdateProfileDto { Age = 30, WeightKg = 75 };
            var updated = new UserProfileDto { Name = "bob", Age = 30, WeightKg = 75 };
            _userServiceMock.Setup(s => s.UpdateProfileAsync(7, dto)).ReturnsAsync(updated);

            var result = await _sut.UpdateMyProfile(dto);

            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsType<UserProfileDto>(ok.Value);
            Assert.Equal(30, returned.Age);
        }

        [Fact]
        public async Task UpdateMyProfile_WhenUserNotFound_ReturnsNotFound()
        {
            SetUserContext("7");
            _userServiceMock.Setup(s => s.UpdateProfileAsync(7, It.IsAny<UpdateProfileDto>()))
                .ReturnsAsync((UserProfileDto?)null);

            var result = await _sut.UpdateMyProfile(new UpdateProfileDto());

            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task UpdateMyProfile_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            SetUserContext(null);

            var result = await _sut.UpdateMyProfile(new UpdateProfileDto());

            Assert.IsType<UnauthorizedResult>(result);
            _userServiceMock.Verify(s => s.UpdateProfileAsync(It.IsAny<int>(), It.IsAny<UpdateProfileDto>()), Times.Never);
        }
    }
}
