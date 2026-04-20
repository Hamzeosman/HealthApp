using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IRecommendationRepository
    {
        Task<IEnumerable<Recommendation>> GetByUserIdAsync(int userId);
        Task<Recommendation?> GetByIdAsync(int id);
        Task AddAsync(Recommendation recommendation);
        Task MarkAsSeenAsync(int id);
        Task SaveChangesAsync();
    }
}