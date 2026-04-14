using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IWorkoutSessionService
    {
        Task<IEnumerable<WorkoutSession>> GetByUserIdAsync(int userId);
        Task<WorkoutSession?> GetByIdAsync(int id);
        Task AddWorkoutSessionAsync(WorkoutSession session);
    }
}