using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class UserProgressService : IUserProgressService
    {
        private readonly IUserProgressRepository _repository;

        public UserProgressService(IUserProgressRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<UserProgress>> GetByUserIdAsync(int userId)
            => await _repository.GetByUserIdAsync(userId);

        public async Task<UserProgress?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(UserProgress progress)
        {
            await _repository.AddAsync(progress);
            await _repository.SaveChangesAsync();
        }
    }
}