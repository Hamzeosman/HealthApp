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
    public class UserProgressControllerTests
    {
        private readonly Mock<IUserProgressService> _serviceMock;
        private readonly UserProgressController _sut;

        // Sätts av GivenServiceCapturesUserIdAtCallTime() — värdet på progress.UserId
        // i exakt det ögonblick då tjänsten anropas (inte efteråt).
        private int? _userIdAtServiceCall;

        public UserProgressControllerTests()
        {
            _serviceMock = new Mock<IUserProgressService>();
            _sut = new UserProgressController(_serviceMock.Object);
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

        // Läser progress.UserId i en Callback, d.v.s. när AddAsync anropas. Det bevisar
        // ORDNINGEN (UserId sätts före tjänsten anropas). En Verify med It.Is<...>
        // utvärderas först efteråt och skulle även passera om tilldelningen låg efter AddAsync.
        private void GivenServiceCapturesUserIdAtCallTime()
        {
            _serviceMock
                .Setup(s => s.AddAsync(It.IsAny<UserProgress>()))
                .Callback<UserProgress>(p => _userIdAtServiceCall = p.UserId);
        }

        // ============================================================
        // GetMyProgress — /me-pattern (regression)
        // ============================================================

        [Fact]
        public async Task GetMyProgress_WithValidUserId_ReturnsOkWithProgress()
        {
            // Arrange
            SetUserContext("42");
            var records = new List<UserProgress>
            {
                new UserProgressBuilder().WithUserId(42).WithId(1).Build()
            };
            _serviceMock.Setup(s => s.GetByUserIdAsync(42)).ReturnsAsync(records);

            // Act
            var result = await _sut.GetMyProgress();

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<UserProgress>>(ok.Value);
            Assert.Single(returned);
        }

        [Fact]
        public async Task GetMyProgress_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);

            // Act
            var result = await _sut.GetMyProgress();

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(It.IsAny<int>()), Times.Never);
        }

        // ============================================================
        // GetByUserId — legacy /user/{userId} med ownership-check (Issue #81)
        // ============================================================

        [Fact]
        public async Task GetByUserId_WhenRequestingOwnRecords_ReturnsOk()
        {
            // Arrange — user 42 frågar efter sina egna records via legacy-endpointen
            SetUserContext("42");
            var records = new List<UserProgress>
            {
                new UserProgressBuilder().WithUserId(42).Build()
            };
            _serviceMock.Setup(s => s.GetByUserIdAsync(42)).ReturnsAsync(records);

            // Act
#pragma warning disable CS0618 // Testar medvetet obsolete endpoint
            var result = await _sut.GetByUserId(42);
#pragma warning restore CS0618

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<UserProgress>>(ok.Value);
            Assert.Single(returned);
        }

        [Fact]
        public async Task GetByUserId_WhenDifferentUser_ReturnsNotFound()
        {
            // Arrange — IDOR-skydd (Issue #81): user 42 försöker läsa user 99:s progress
            // via legacy /user/{userId}-endpointen. Ska returnera NotFound och ALDRIG
            // anropa service — samma pattern som övriga ownership-checkar.
            SetUserContext("42");

            // Act
#pragma warning disable CS0618
            var result = await _sut.GetByUserId(99);
#pragma warning restore CS0618

            // Assert
            Assert.IsType<NotFoundResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(It.IsAny<int>()), Times.Never);
        }

        [Fact]
        public async Task GetByUserId_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange — saknad JWT → Unauthorized, service anropas aldrig
            SetUserContext(null);

            // Act
#pragma warning disable CS0618
            var result = await _sut.GetByUserId(42);
#pragma warning restore CS0618

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(It.IsAny<int>()), Times.Never);
        }

        // ============================================================
        // GetById — ownership-check (Issue #81, KRITISK — tidigare HELT osäker)
        // ============================================================

        [Fact]
        public async Task GetById_WhenOwnerMatches_ReturnsOk()
        {
            // Arrange — user 42 hämtar sin egen progress-post
            SetUserContext("42");
            var progress = new UserProgressBuilder().WithId(7).WithUserId(42).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync(progress);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsType<UserProgress>(ok.Value);
            Assert.Equal(7, returned.Id);
        }

        [Fact]
        public async Task GetById_WhenDifferentOwner_ReturnsNotFound()
        {
            // Arrange — KRITISK IDOR-fix (Issue #81). Tidigare kunde ANY user läsa 
            // ANY progress-post genom att gissa en id. Nu returnerar vi NotFound 
            // (inte Forbidden) för att inte avslöja att id:t existerar.
            SetUserContext("42");
            var progress = new UserProgressBuilder().WithId(7).WithUserId(99).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync(progress);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetById_WhenProgressNotFound_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock.Setup(s => s.GetByIdAsync(999)).ReturnsAsync((UserProgress?)null);

            // Act
            var result = await _sut.GetById(999);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetById_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange — saknad JWT → Unauthorized, service anropas aldrig
            SetUserContext(null);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByIdAsync(It.IsAny<int>()), Times.Never);
        }

        // ============================================================
        // Add — JWT-override (regression)
        // ============================================================

        [Fact]
        public async Task Add_WithValidJwt_SetsUserIdFromClaimAndReturnsCreated()
        {
            // Arrange — user 42 är inloggad, body har samma userId
            SetUserContext("42");
            var progress = new UserProgressBuilder()
                .WithUserId(42)
                .WithWeight(75m)
                .Build();

            // Act
            var result = await _sut.Add(progress);

            // Assert
            var created = Assert.IsType<CreatedAtActionResult>(result);
            var returned = Assert.IsType<UserProgress>(created.Value);
            Assert.Equal(42, returned.UserId);
            _serviceMock.Verify(s => s.AddAsync(It.Is<UserProgress>(p => p.UserId == 42)), Times.Once);
        }

        [Fact]
        public async Task Add_WhenBodyHasDifferentUserId_OverridesWithJwtUserId()
        {
            // Arrange — user 42 inloggad men försöker skapa progress åt user 99 (säkerhetstest)
            SetUserContext("42");
            GivenServiceCapturesUserIdAtCallTime();
            var progress = new UserProgressBuilder()
                .WithUserId(99)
                .WithWeight(75m)
                .Build();

            // Act
            var result = await _sut.Add(progress);

            // Assert — UserId ska vara överskrivet med JWT-user (42) REDAN när tjänsten anropas.
            // Läses i en Callback, så testet faller om tilldelningen flyttas efter AddAsync.
            Assert.Equal(42, _userIdAtServiceCall);
            _serviceMock.Verify(s => s.AddAsync(It.IsAny<UserProgress>()), Times.Once);

            var created = Assert.IsType<CreatedAtActionResult>(result);
            var returned = Assert.IsType<UserProgress>(created.Value);
            Assert.Equal(42, returned.UserId);
        }

        [Fact]
        public async Task Add_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);
            var progress = new UserProgressBuilder().Build();

            // Act
            var result = await _sut.Add(progress);

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.AddAsync(It.IsAny<UserProgress>()), Times.Never);
        }
    }
}