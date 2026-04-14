using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IWorkoutSessionRepository
    {
        Task<IEnumerable<WorkoutSession>> GetByUserIdAsync(int userId);
        Task<WorkoutSession?> GetByIdAsync(int id);
        Task AddAsync(WorkoutSession session);
        Task SaveChangesAsync();
    }
}