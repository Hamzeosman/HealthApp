using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IWorkoutTemplateService
    {
        Task<IEnumerable<WorkoutTemplate>> GetByProgramIdAsync(int programId);
        Task<WorkoutTemplate?> GetByIdAsync(int id);
        Task AddAsync(WorkoutTemplate template);
    }
}