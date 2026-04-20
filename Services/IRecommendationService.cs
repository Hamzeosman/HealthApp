using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IRecommendationService
    {
        Task<IEnumerable<Recommendation>> GetByUserIdAsync(int userId);
        Task<Recommendation?> GetByIdAsync(int id);
        Task AddAsync(Recommendation recommendation);
        Task MarkAsSeenAsync(int id);
    }
}