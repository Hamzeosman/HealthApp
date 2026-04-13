using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class UserRepository : IUserRepository
    {
        private readonly AppDbContext _context;

        public UserRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<User?> GetByUsernameAsync(string username)
            => await _context.Users
                .FirstOrDefaultAsync(u => u.Username.ToLower() == username.ToLower());

        public async Task<User?> GetByIdAsync(int id)
            => await _context.Users.FindAsync(id);

        public async Task AddAsync(User user)
            => await _context.Users.AddAsync(user);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}