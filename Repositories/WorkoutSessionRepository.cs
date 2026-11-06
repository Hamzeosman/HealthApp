using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    /// <summary>
    /// Repository för WorkoutSessionData mot DataDbContext (HealthAppDataDb, snake_case).
    ///
    /// Historik: Tidigare använde denna AppDbContext (PascalCase/HealthAppDb) med den gamla
    /// WorkoutSession-modellen. Det ledde till bug (Issue #68) där POST skrev till ena DB:n
    /// men GET läste från den andra. Fixat i PR genom att byta till DataDbContext +
    /// WorkoutSessionData som Abdulrahman förberedde i Issue #32.
    /// </summary>
    public class WorkoutSessionRepository : IWorkoutSessionRepository
    {
        private readonly DataDbContext _context;

        public WorkoutSessionRepository(DataDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<WorkoutSessionData>> GetByUserIdAsync(int userId)
            => await _context.WorkoutSessions
                .Include(w => w.WorkoutExercises)
                    .ThenInclude(we => we.Exercise)
                .Where(w => w.UserId == userId)
                .OrderByDescending(w => w.Date)
                .ToListAsync();

        public async Task<WorkoutSessionData?> GetByIdAsync(int id)
            => await _context.WorkoutSessions
                .Include(w => w.WorkoutExercises)
                    .ThenInclude(we => we.Exercise)
                .FirstOrDefaultAsync(w => w.Id == id);

        public async Task AddAsync(WorkoutSessionData session)
            => await _context.WorkoutSessions.AddAsync(session);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}