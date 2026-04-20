using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IUserProgressRepository
    {
        Task<IEnumerable<UserProgress>> GetByUserIdAsync(int userId);
        Task<UserProgress?> GetByIdAsync(int id);
        Task AddAsync(UserProgress progress);
        Task SaveChangesAsync();
    }
}