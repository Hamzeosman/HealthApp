using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    public interface IWorkoutSessionService
    {
        Task<IEnumerable<WorkoutSessionDto>> GetByUserIdAsync(int userId);
        Task<WorkoutSessionDto?> GetByIdAsync(int id);
        Task<WorkoutSessionDto> AddWorkoutSessionAsync(CreateWorkoutSessionDto dto);
    }
}