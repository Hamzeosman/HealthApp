using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    public interface IAuthService
    {
        Task<string?> RegisterAsync(RegisterDto dto);
        Task<string?> LoginAsync(LoginDto dto);
    }
}