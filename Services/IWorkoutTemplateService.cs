using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IWorkoutTemplateService
    {
        Task<IEnumerable<WorkoutTemplate>> GetByProgramIdAsync(int programId);
        Task<WorkoutTemplate?> GetByIdAsync(int id);
        Task AddAsync(WorkoutTemplate template);
    }
}