using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IExerciseRepository
    {
        Task<IEnumerable<Exercise>> GetAllAsync();
        Task<IEnumerable<Exercise>> GetByMuscleGroupAsync(string muscleGroup);
        Task<Exercise?> GetByIdAsync(int id);
        Task AddAsync(Exercise exercise);
        Task SaveChangesAsync();
    }
}