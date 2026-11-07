namespace Mintakt.API.Helpers
{
    /// <summary>
    /// Avgör vilka webbadresser som får anropa API:et från en webbläsare.
    ///
    /// Adresserna i Cors:AllowedOrigins tillåts alltid. I utvecklingsläge tillåts också
    /// localhost och 127.0.0.1 på alla portar, eftersom varje worktree får en egen klientport.
    /// </summary>
    public static class CorsOrigins
    {
        public static bool IsAllowed(string? origin, IEnumerable<string> configuredOrigins, bool isDevelopment)
        {
            if (string.IsNullOrWhiteSpace(origin)) return false;

            var normalized = origin.TrimEnd('/');
            if (configuredOrigins.Any(o => string.Equals(o.TrimEnd('/'), normalized, StringComparison.OrdinalIgnoreCase)))
                return true;

            if (!isDevelopment) return false;
            if (!Uri.TryCreate(origin, UriKind.Absolute, out var uri)) return false;
            if (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps) return false;

            return uri.Host == "localhost" || uri.Host == "127.0.0.1";
        }
    }
}
