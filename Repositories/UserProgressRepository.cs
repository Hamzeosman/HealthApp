using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class UserProgressRepository : IUserProgressRepository
    {
        private readonly AppDbContext _context;

        public UserProgressRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<UserProgress>> GetByUserIdAsync(int userId)
            => await _context.UserProgressList
                .Where(p => p.UserId == userId)
                .OrderByDescending(p => p.Date)
                .ToListAsync();

        public async Task<UserProgress?> GetByIdAsync(int id)
            => await _context.UserProgressList.FindAsync(id);

        public async Task AddAsync(UserProgress progress)
            => await _context.UserProgressList.AddAsync(progress);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}