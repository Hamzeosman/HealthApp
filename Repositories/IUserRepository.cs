using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IUserRepository
    {
        Task<User?> GetByUsernameAsync(string username);
        Task<User?> GetByIdAsync(int id);
        Task AddAsync(User user);
        Task SaveChangesAsync();
    }
}