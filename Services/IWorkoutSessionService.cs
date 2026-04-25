using HealthApp.API.DTOs;

namespace HealthApp.API.Services
{
    public interface IWorkoutSessionService
    {
        Task<IEnumerable<WorkoutSessionDto>> GetByUserIdAsync(int userId);
        Task<WorkoutSessionDto?> GetByIdAsync(int id);
        Task<WorkoutSessionDto> AddWorkoutSessionAsync(CreateWorkoutSessionDto dto);
    }
}