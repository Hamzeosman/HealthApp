using Mintakt.API.Helpers;
using Xunit;

namespace HealthApp.Tests.Helpers
{
    public class CorsOriginsTests
    {
        private static readonly string[] Configured = { "http://localhost:5028" };

        // Den konfigurerade frontend-adressen tillåts i alla miljöer
        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void IsAllowed_WithConfiguredOrigin_ReturnsTrue(bool isDevelopment)
        {
            Assert.True(CorsOrigins.IsAllowed("http://localhost:5028", Configured, isDevelopment));
        }

        // Konfigurerade adresser jämförs utan avslutande snedstreck och utan skiftläge
        [Fact]
        public void IsAllowed_WithTrailingSlashInConfig_ReturnsTrue()
        {
            Assert.True(CorsOrigins.IsAllowed("http://LOCALHOST:5028", new[] { "http://localhost:5028/" }, false));
        }

        // Varje worktree får en egen klientport, så alla lokala portar tillåts i utvecklingsläge
        [Theory]
        [InlineData("http://localhost:6431")]
        [InlineData("http://127.0.0.1:5900")]
        [InlineData("https://localhost:7208")]
        public void IsAllowed_WithLocalOriginInDevelopment_ReturnsTrue(string origin)
        {
            Assert.True(CorsOrigins.IsAllowed(origin, Configured, isDevelopment: true));
        }

        // Utanför utvecklingsläge gäller bara den konfigurerade listan
        [Fact]
        public void IsAllowed_WithLocalOriginOutsideDevelopment_ReturnsFalse()
        {
            Assert.False(CorsOrigins.IsAllowed("http://localhost:6431", Configured, isDevelopment: false));
        }

        // Säkerhet: värdnamn som bara liknar localhost släpps aldrig igenom
        [Theory]
        [InlineData("http://localhost.example.com")]
        [InlineData("http://example.com")]
        [InlineData("http://localhost:6431.example.com")]
        [InlineData("file://localhost")]
        [InlineData("not a url")]
        [InlineData("")]
        [InlineData(null)]
        public void IsAllowed_WithForeignOrInvalidOrigin_ReturnsFalse(string? origin)
        {
            Assert.False(CorsOrigins.IsAllowed(origin, Configured, isDevelopment: true));
        }
    }
}
