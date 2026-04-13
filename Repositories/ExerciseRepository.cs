using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class ExerciseRepository : IExerciseRepository
    {
        private readonly AppDbContext _context;

        public ExerciseRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Exercise>> GetAllAsync()
            => await _context.Exercises.ToListAsync();

        public async Task<IEnumerable<Exercise>> GetByMuscleGroupAsync(string muscleGroup)
            => await _context.Exercises
                .Where(e => e.MuscleGroup != null && e.MuscleGroup.Name.ToLower() == muscleGroup.ToLower())
                .ToListAsync();

        public async Task<Exercise?> GetByIdAsync(int id)
            => await _context.Exercises.FindAsync(id);

        public async Task AddAsync(Exercise exercise)
            => await _context.Exercises.AddAsync(exercise);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}