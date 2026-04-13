using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IUserRepository
    {
        Task<User?> GetByUsernameAsync(string username);
        Task<User?> GetByIdAsync(int id);
        Task AddAsync(User user);
        Task SaveChangesAsync();
    }
}