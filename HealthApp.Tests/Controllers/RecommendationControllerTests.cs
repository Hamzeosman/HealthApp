using System.Security.Claims;
using HealthApp.Tests.Builders;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Controllers;
using Mintakt.API.Models;
using Mintakt.API.Services;
using Moq;

namespace HealthApp.Tests.Controllers
{
    public class RecommendationControllerTests
    {
        private readonly Mock<IRecommendationService> _serviceMock;
        private readonly RecommendationController _sut;

        public RecommendationControllerTests()
        {
            _serviceMock = new Mock<IRecommendationService>();
            _sut = new RecommendationController(_serviceMock.Object);
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

        // ─── GetMe tests ─────────────────────────────────────────────────

        // Happy path: inloggad user får sina rekommendationer
        [Fact]
        public async Task GetMe_WithValidUserId_ReturnsOkWithRecommendations()
        {
            // Arrange
            SetUserContext("42");
            var recs = new[] { new RecommendationBuilder().WithUserId(42).Build() };
            _serviceMock.Setup(s => s.GetByUserIdAsync(42)).ReturnsAsync(recs);

            // Act
            var result = await _sut.GetMe();

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<Recommendation>>(ok.Value);
            Assert.Single(returned);
        }

        // Felfall: saknas JWT-claim → Unauthorized + service anropas aldrig
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

        // Edge case: tom lista från service → Ok med tom lista (inte 404)
        [Fact]
        public async Task GetMe_WhenServiceReturnsEmpty_ReturnsOkWithEmptyList()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock.Setup(s => s.GetByUserIdAsync(42))
                .ReturnsAsync(Array.Empty<Recommendation>());

            // Act
            var result = await _sut.GetMe();

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<Recommendation>>(ok.Value);
            Assert.Empty(returned);
        }

        // ─── GetByUserId tests (legacy, nu med ownership-check) ─────────

        // Happy path: inloggad user frågar efter sina egna records
        [Fact]
        public async Task GetByUserId_WhenRequestingOwnRecords_ReturnsOk()
        {
            // Arrange
            SetUserContext("42");
            var recs = new[] { new RecommendationBuilder().WithUserId(42).Build() };
            _serviceMock.Setup(s => s.GetByUserIdAsync(42)).ReturnsAsync(recs);

            // Act
#pragma warning disable CS0618 // Testar medvetet obsolete endpoint
            var result = await _sut.GetByUserId(42);
#pragma warning restore CS0618

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsAssignableFrom<IEnumerable<Recommendation>>(ok.Value);
            Assert.Single(returned);
        }

        // KRITISK (Issue #82): IDOR-skydd — kan inte läsa annans rekommendationer
        [Fact]
        public async Task GetByUserId_WhenDifferentUser_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");

            // Act
#pragma warning disable CS0618
            var result = await _sut.GetByUserId(99);
#pragma warning restore CS0618

            // Assert
            Assert.IsType<NotFoundResult>(result);
            _serviceMock.Verify(s => s.GetByUserIdAsync(It.IsAny<int>()), Times.Never);
        }

        // Felfall: saknas JWT-claim → Unauthorized
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

        // ─── GetById tests (regression — redan säker sedan tidigare) ────

        // Happy path: user hämtar sin egen rekommendation
        [Fact]
        public async Task GetById_WhenOwnerMatches_ReturnsOk()
        {
            // Arrange
            SetUserContext("42");
            var rec = new RecommendationBuilder().WithId(7).WithUserId(42).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync(rec);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            var ok = Assert.IsType<OkObjectResult>(result);
            var returned = Assert.IsType<Recommendation>(ok.Value);
            Assert.Equal(7, returned.Id);
        }

        // IDOR-skydd: returnerar NotFound (inte Forbidden) för att inte
        // avslöja att ID:t existerar för en annan user
        [Fact]
        public async Task GetById_WhenDifferentOwner_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            var rec = new RecommendationBuilder().WithId(7).WithUserId(99).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync(rec);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        // Edge case: rekommendation finns inte → NotFound
        [Fact]
        public async Task GetById_WhenRecommendationNotFound_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync((Recommendation?)null);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        // Felfall: saknas JWT-claim → Unauthorized
        [Fact]
        public async Task GetById_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);

            // Act
            var result = await _sut.GetById(7);

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.GetByIdAsync(It.IsAny<int>()), Times.Never);
        }

        // ─── MarkAsSeen tests (regression — redan säker) ─────────────────

        // Happy path: user markerar sin egen rekommendation som sedd
        [Fact]
        public async Task MarkAsSeen_WhenOwnerMatches_ReturnsNoContent()
        {
            // Arrange
            SetUserContext("42");
            var rec = new RecommendationBuilder().WithId(7).WithUserId(42).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync(rec);

            // Act
            var result = await _sut.MarkAsSeen(7);

            // Assert
            Assert.IsType<NoContentResult>(result);
            _serviceMock.Verify(s => s.MarkAsSeenAsync(7), Times.Once);
        }

        // IDOR-skydd: kan inte markera annans rekommendation
        [Fact]
        public async Task MarkAsSeen_WhenDifferentOwner_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            var rec = new RecommendationBuilder().WithId(7).WithUserId(99).Build();
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync(rec);

            // Act
            var result = await _sut.MarkAsSeen(7);

            // Assert
            Assert.IsType<NotFoundResult>(result);
            _serviceMock.Verify(s => s.MarkAsSeenAsync(It.IsAny<int>()), Times.Never);
        }

        // Edge case: rekommendation finns inte → NotFound, ingen update
        [Fact]
        public async Task MarkAsSeen_WhenRecommendationNotFound_ReturnsNotFound()
        {
            // Arrange
            SetUserContext("42");
            _serviceMock.Setup(s => s.GetByIdAsync(7)).ReturnsAsync((Recommendation?)null);

            // Act
            var result = await _sut.MarkAsSeen(7);

            // Assert
            Assert.IsType<NotFoundResult>(result);
            _serviceMock.Verify(s => s.MarkAsSeenAsync(It.IsAny<int>()), Times.Never);
        }

        // Felfall: saknas JWT-claim → Unauthorized
        [Fact]
        public async Task MarkAsSeen_WhenNoUserIdClaim_ReturnsUnauthorized()
        {
            // Arrange
            SetUserContext(null);

            // Act
            var result = await _sut.MarkAsSeen(7);

            // Assert
            Assert.IsType<UnauthorizedResult>(result);
            _serviceMock.Verify(s => s.MarkAsSeenAsync(It.IsAny<int>()), Times.Never);
        }
    }
}