using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IWorkoutTemplateRepository
    {
        Task<IEnumerable<WorkoutTemplate>> GetByProgramIdAsync(int programId);
        Task<WorkoutTemplate?> GetByIdAsync(int id);
        Task AddAsync(WorkoutTemplate template);
        Task SaveChangesAsync();
    }
}