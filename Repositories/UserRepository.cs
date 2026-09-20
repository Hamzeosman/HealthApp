using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API.Repositories
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
                .FirstOrDefaultAsync(u => u.Name.ToLower() == username.ToLower());

        public async Task<User?> GetByIdAsync(int id)
            => await _context.Users.FindAsync(id);

        public async Task AddAsync(User user)
            => await _context.Users.AddAsync(user);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}