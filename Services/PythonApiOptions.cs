namespace HealthApp.API.Services
{
    // Options-klass för PythonApiClient-konfiguration.
    // Binds mot "PythonApi"-sektionen i appsettings.json via IOptions<T>.
    //
    // ApiKey läses ALDRIG från appsettings.json — konfigureras via
    // dotnet user-secrets (dev) eller miljövariabler (production) för
    // att undvika att credentials committas till repo:t.
    // Se chore-issue #40 för planerad credential-hantering.
    public class PythonApiOptions
    {
        public const string SectionName = "PythonApi";

        public string BaseUrl { get; set; } = string.Empty;
        public string ApiKey { get; set; } = string.Empty;
        public int TimeoutSeconds { get; set; } = 30;
    }
}