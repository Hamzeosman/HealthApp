using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IWorkoutProgramRepository
    {
        Task<IEnumerable<WorkoutProgram>> GetAllAsync();
        Task<WorkoutProgram?> GetByIdAsync(int id);
        Task AddAsync(WorkoutProgram program);
        Task SaveChangesAsync();
    }
}