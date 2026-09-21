using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IWorkoutProgramService
    {
        Task<IEnumerable<WorkoutProgram>> GetAllAsync();
        Task<WorkoutProgram?> GetByIdAsync(int id);
        Task AddAsync(WorkoutProgram program);
    }
}