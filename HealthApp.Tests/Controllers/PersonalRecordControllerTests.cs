using System.Security.Claims;
using HealthApp.Tests.Builders;
using Mintakt.API.Controllers;
using Mintakt.API.Models;
using Mintakt.API.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Moq;

namespace HealthApp.Tests.Controllers
{
    public class PersonalRecordControllerTests
    {
        private readonly Mock<IPersonalRecordService> _serviceMock;
        private readonly PersonalRecordController _sut;

        public PersonalRecordControllerTests()
        {
            _serviceMock = new Mock<IPersonalRecordService>();
            _sut = new PersonalRecordController(_serviceMock.Object);
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
        // Add — JWT-override (PR A3c huvudfokus)
        // ============================================================

        [Fact]
        public async Task Add_WithValidJwt_SetsUserIdFromClaimAndReturnsCreated()
        {
            // Arrange — user 42 är inloggad, body har samma userId
            SetUserContext("42");
            var record = new PersonalRecordBuilder()
                .WithUserId(42)
                .WithExerciseId(10)
                .WithWeight(120m)
                .WithReps(3)
                .Build();

            // Act
            var result = await _sut.Add(record);

            // Assert
            var created = Assert.IsType<CreatedAtActionResult>(result);
            var returned = Assert.IsType<PersonalRecord>(created.Value);
            Assert.Equal(42, returned.UserId);
            _serviceMock.Verify(s => s.AddAsync(It.Is<PersonalRecord>(r => r.UserId == 42)), Times.Once);
        }

        [Fact]
        public async Task Add_WhenBodyHasDifferentUserId_OverridesWithJwtUserId()
        {
            // Arrange — user 42 inloggad men försöker skapa PR åt user 99 (säkerhetstest)
            SetUserContext("42");
            var record = new PersonalRecordBuilder()
                .WithUserId(99)
                .WithExerciseId(10)
                .WithWeight(120m)
                .Build();

            // Act
            var result = await _sut.Add(record);

            // Assert — body-UserId ska skrivas över med JWT-user (42)
            var created = Assert.IsType<CreatedAtActionResult>(result);
            var returned = Assert.IsType<PersonalRecord>(created.Value);
            Assert.Equal(42, returned.UserId);
            Assert.NotEqual(99, returned.UserId);
            _serviceMock.Verify(s => s.AddAsync(It.Is<PersonalRecord>(r => r.UserId == 42)), Times.Once);
            _serviceMock.Verify(s => s.AddAsync(It.Is<PersonalRecord>(r => r.UserId == 99)), Times.Never);
        }

        [Fact]
        public async Task Add_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);
            var record = new PersonalRecordBuilder().Build();

            // Act
            var result = await _sut.Add(record);

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
        }

        [Fact]
        public async Task Add_WhenNoUserIdClaim_DoesNotCallService()
        {
            // Arrange
            SetUserContext(null);
            var record = new PersonalRecordBuilder().Build();

            // Act
            await _sut.Add(record);

            // Assert — service ska ALDRIG anropas utan auth
            _serviceMock.Verify(s => s.AddAsync(It.IsAny<PersonalRecord>()), Times.Never);
        }

        // ============================================================
        // GetMe — /me-pattern (PR A3b, regression-tester)
        // ============================================================

        [Fact]
        public async Task GetMe_WithValidJwt_ReturnsRecordsForAuthenticatedUser()
        {
            // Arrange
            SetUserContext("42");
            var records = new List<PersonalRecord>
            {
                new PersonalRecordBuilder().WithUserId(42).WithId(1).Build(),
                new PersonalRecordBuilder().WithUserId(42).WithId(2).Build()
            };
            _serviceMock.Setup(s => s.GetByUserIdAsync(42)).ReturnsAsync(records);

            // Act
            var result = await _sut.GetMe();

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<PersonalRecord>>(ok.Value);
            Assert.Equal(2, returned.Count());
        }

        [Fact]
        public async Task GetMe_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);

            // Act
            var result = await _sut.GetMe();

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(It.IsAny<int>()), Times.Never);
        }

        // ============================================================
        // GetById — ownership-check (PR A3a, regression-tester)
        // ============================================================

        [Fact]
        public async Task GetById_WhenRecordBelongsToSameUser_ReturnsOk()
        {
            // Arrange
            SetUserContext("42");
            var record = new PersonalRecordBuilder().WithId(5).WithUserId(42).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(5)).ReturnsAsync(record);

            // Act
            var result = await _sut.GetById(5);

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsType<PersonalRecord>(ok.Value);
            Assert.Equal(5, returned.Id);
        }

        [Fact]
        public async Task GetById_WhenRecordBelongsToAnotherUser_ReturnsNotFound()
        {
            // Arrange — IDOR-skydd: NotFound istället för Forbidden för att undvika
            // att avslöja att record-ID existerar för någon annan user
            SetUserContext("42");
            var record = new PersonalRecordBuilder().WithId(5).WithUserId(99).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(5)).ReturnsAsync(record);

            // Act
            var result = await _sut.GetById(5);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetById_WhenRecordDoesNotExist_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock.Setup(s => s.GetByIdAsync(999)).ReturnsAsync((PersonalRecord?)null);

            // Act
            var result = await _sut.GetById(999);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }
    }
}