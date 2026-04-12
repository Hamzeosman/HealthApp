using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class WorkoutSessionService : IWorkoutSessionService
    {
        private readonly IWorkoutSessionRepository _repository;

        public WorkoutSessionService(IWorkoutSessionRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<WorkoutSession>> GetByUserIdAsync(int userId)
            => await _repository.GetByUserIdAsync(userId);

        public async Task<WorkoutSession?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddWorkoutSessionAsync(WorkoutSession session)
        {
            await _repository.AddAsync(session);
            await _repository.SaveChangesAsync();
        }
    }
}