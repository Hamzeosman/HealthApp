using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class RecommendationService : IRecommendationService
    {
        private readonly IRecommendationRepository _repository;

        public RecommendationService(IRecommendationRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<Recommendation>> GetByUserIdAsync(int userId)
            => await _repository.GetByUserIdAsync(userId);

        public async Task<Recommendation?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(Recommendation recommendation)
        {
            await _repository.AddAsync(recommendation);
            await _repository.SaveChangesAsync();
        }

        public async Task MarkAsSeenAsync(int id)
        {
            await _repository.MarkAsSeenAsync(id);
            await _repository.SaveChangesAsync();
        }
    }
}