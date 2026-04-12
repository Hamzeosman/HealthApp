using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class WorkoutSessionRepository : IWorkoutSessionRepository
    {
        private readonly AppDbContext _context;

        public WorkoutSessionRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<WorkoutSession>> GetByUserIdAsync(int userId)
            => await _context.WorkoutSessions
                .Include(w => w.WorkoutExercises)
                .Where(w => w.UserId == userId)
                .ToListAsync();

        public async Task<WorkoutSession?> GetByIdAsync(int id)
            => await _context.WorkoutSessions
                .Include(w => w.WorkoutExercises)
                .FirstOrDefaultAsync(w => w.Id == id);

        public async Task AddAsync(WorkoutSession session)
            => await _context.WorkoutSessions.AddAsync(session);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}