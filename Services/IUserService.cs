using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    public interface IUserService
    {
        Task<UserProfileDto?> GetProfileAsync(int userId);
        Task<UserProfileDto?> UpdateProfileAsync(int userId, UpdateProfileDto dto);
    }
}
