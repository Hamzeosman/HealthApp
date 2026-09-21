using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IUserProgressRepository
    {
        Task<IEnumerable<UserProgress>> GetByUserIdAsync(int userId);
        Task<UserProgress?> GetByIdAsync(int id);
        Task AddAsync(UserProgress progress);
        Task SaveChangesAsync();
    }
}