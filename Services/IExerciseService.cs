using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IExerciseService
    {
        Task<IEnumerable<Exercise>> GetAllExercisesAsync();
        Task<IEnumerable<Exercise>> GetByMuscleGroupAsync(string muscleGroup);
        Task<Exercise?> GetByIdAsync(int id);
        Task AddExerciseAsync(Exercise exercise);
    }
}