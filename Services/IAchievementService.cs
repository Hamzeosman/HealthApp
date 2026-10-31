using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    public interface IAchievementService
    {
        Task<IEnumerable<AchievementStatusDto>> GetUserAchievementsAsync(int userId);
    }
}
