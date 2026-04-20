using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IWorkoutProgramService
    {
        Task<IEnumerable<WorkoutProgram>> GetAllAsync();
        Task<WorkoutProgram?> GetByIdAsync(int id);
        Task AddAsync(WorkoutProgram program);
    }
}