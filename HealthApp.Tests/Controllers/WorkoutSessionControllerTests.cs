using System.Security.Claims;
using HealthApp.Tests.Builders;
using Mintakt.API.Controllers;
using Mintakt.API.DTOs;
using Mintakt.API.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Moq;

namespace HealthApp.Tests.Controllers
{
    public class WorkoutSessionControllerTests
    {
        private readonly Mock<IWorkoutSessionService> _serviceMock;
        private readonly WorkoutSessionController _sut;

        public WorkoutSessionControllerTests()
        {
            _serviceMock = new Mock<IWorkoutSessionService>();
            _sut = new WorkoutSessionController(_serviceMock.Object);
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

        // ============================================================
        // GetById — ownership-check (issue #75)
        // ============================================================

        // Eget pass ska returneras med 200.
        [Fact]
        public async Task GetById_WhenSessionBelongsToSameUser_ReturnsOk()
        {
            // Arrange
            SetUserContext("42");
            var session = new WorkoutSessionDtoBuilder().WithId(5).WithUserId(42).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(5)).ReturnsAsync(session);

            // Act
            var result = await _sut.GetById(5);

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsType<WorkoutSessionDto>(ok.Value);
            Assert.Equal(5, returned.Id);
        }

        // IDOR-skydd: NotFound istället för Forbidden så att vi inte avslöjar
        // att pass-ID:t finns hos en annan användare.
        [Fact]
        public async Task GetById_WhenSessionBelongsToAnotherUser_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            var session = new WorkoutSessionDtoBuilder().WithId(5).WithUserId(99).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(5)).ReturnsAsync(session);

            // Act
            var result = await _sut.GetById(5);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        // Pass som inte finns ska ge 404.
        [Fact]
        public async Task GetById_WhenSessionDoesNotExist_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock.Setup(s => s.GetByIdAsync(999)).ReturnsAsync((WorkoutSessionDto?)null);

            // Act
            var result = await _sut.GetById(999);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        // Utan user-id-claim ska svaret vara 401 och tjänsten ska aldrig anropas.
        // Passet finns och tillhör användare 42, så ett Ok-svar vore ett läckage.
        [Fact]
        public async Task GetById_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);
            var session = new WorkoutSessionDtoBuilder().WithId(5).WithUserId(42).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(5)).ReturnsAsync(session);

            // Act
            var result = await _sut.GetById(5);

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByIdAsync(It.IsAny<int>()), Times.Never);
        }

        // ============================================================
        // GetByUserId — deprecated, ska ändå kräva att userId matchar JWT (issue #75)
        // ============================================================

        // Egen userId i URL matchar JWT och ska ge 200.
        [Fact]
        public async Task GetByUserId_WhenUserIdMatchesJwt_ReturnsOk()
        {
            // Arrange
            SetUserContext("42");
            var sessions = new List<WorkoutSessionDto>
            {
                new WorkoutSessionDtoBuilder().WithId(1).WithUserId(42).Build(),
                new WorkoutSessionDtoBuilder().WithId(2).WithUserId(42).Build()
            };
            _serviceMock.Setup(s => s.GetByUserIdAsync(42)).ReturnsAsync(sessions);

            // Act
#pragma warning disable CS0618
            var result = await _sut.GetByUserId(42);
#pragma warning restore CS0618

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<WorkoutSessionDto>>(ok.Value);
            Assert.Equal(2, returned.Count());
        }

        // Någon annans userId i URL ska ge 404, och tjänsten får aldrig frågas efter den datan.
        [Fact]
        public async Task GetByUserId_WhenUserIdIsAnotherUser_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock
                .Setup(s => s.GetByUserIdAsync(99))
                .ReturnsAsync(new List<WorkoutSessionDto>
                {
                    new WorkoutSessionDtoBuilder().WithUserId(99).Build()
                });

            // Act
#pragma warning disable CS0618
            var result = await _sut.GetByUserId(99);
#pragma warning restore CS0618

            // Assert
            Assert.IsType<NotFoundResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(99), Times.Never);
        }

        // Utan user-id-claim ska svaret vara 401.
        [Fact]
        public async Task GetByUserId_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);

            // Act
#pragma warning disable CS0618
            var result = await _sut.GetByUserId(42);
#pragma warning restore CS0618

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(It.IsAny<int>()), Times.Never);
        }
    }
}
