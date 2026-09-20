using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public class WorkoutTemplateRepository : IWorkoutTemplateRepository
    {
        private readonly AppDbContext _context;

        public WorkoutTemplateRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<WorkoutTemplate>> GetByProgramIdAsync(int programId)
            => await _context.WorkoutTemplates
                .Include(t => t.TemplateExercises)
                .Where(t => t.ProgramId == programId)
                .ToListAsync();

        public async Task<WorkoutTemplate?> GetByIdAsync(int id)
            => await _context.WorkoutTemplates
                .Include(t => t.TemplateExercises)
                .FirstOrDefaultAsync(t => t.Id == id);

        public async Task AddAsync(WorkoutTemplate template)
            => await _context.WorkoutTemplates.AddAsync(template);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}