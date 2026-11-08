using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IWorkoutSessionRepository
    {
        Task<IEnumerable<WorkoutSessionData>> GetByUserIdAsync(int userId);
        Task<WorkoutSessionData?> GetByIdAsync(int id);
        Task AddAsync(WorkoutSessionData session);
        Task SaveChangesAsync();
    }
}