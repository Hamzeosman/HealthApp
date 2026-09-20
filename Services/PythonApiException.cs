using System.Net;

namespace Mintakt.API.Services
{
    // Typed exception för fel från Python API-anrop.
    // Kastas av PythonApiClient när API returnerar icke-success statuskod
    // (utom 404 som konverteras till null/tom lista av klienten).
    //
    // Innehåller aldrig X-API-Key eller andra känsliga headers — bara URL + status
    // för säker loggning utan risk att läcka credentials.
    public class PythonApiException : Exception
    {
        public HttpStatusCode StatusCode { get; }
        public string RequestUri { get; }

        public PythonApiException(string message, HttpStatusCode statusCode, string requestUri)
            : base(message)
        {
            StatusCode = statusCode;
            RequestUri = requestUri;
        }

        public PythonApiException(string message, HttpStatusCode statusCode, string requestUri, Exception innerException)
            : base(message, innerException)
        {
            StatusCode = statusCode;
            RequestUri = requestUri;
        }
    }
}