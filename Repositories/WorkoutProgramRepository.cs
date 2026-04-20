using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class WorkoutProgramRepository : IWorkoutProgramRepository
    {
        private readonly AppDbContext _context;

        public WorkoutProgramRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<WorkoutProgram>> GetAllAsync()
            => await _context.WorkoutPrograms
                .Include(p => p.WorkoutTemplates)
                .ToListAsync();

        public async Task<WorkoutProgram?> GetByIdAsync(int id)
            => await _context.WorkoutPrograms
                .Include(p => p.WorkoutTemplates)
                .FirstOrDefaultAsync(p => p.Id == id);

        public async Task AddAsync(WorkoutProgram program)
            => await _context.WorkoutPrograms.AddAsync(program);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}