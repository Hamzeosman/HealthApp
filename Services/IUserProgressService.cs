using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IUserProgressService
    {
        Task<IEnumerable<UserProgress>> GetByUserIdAsync(int userId);
        Task<UserProgress?> GetByIdAsync(int id);
        Task AddAsync(UserProgress progress);
    }
}