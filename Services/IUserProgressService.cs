using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IUserProgressService
    {
        Task<IEnumerable<UserProgress>> GetByUserIdAsync(int userId);
        Task<UserProgress?> GetByIdAsync(int id);
        Task AddAsync(UserProgress progress);
    }
}