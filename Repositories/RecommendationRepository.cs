using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class RecommendationRepository : IRecommendationRepository
    {
        private readonly AppDbContext _context;

        public RecommendationRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Recommendation>> GetByUserIdAsync(int userId)
            => await _context.Recommendations
                .Where(r => r.UserId == userId)
                .OrderByDescending(r => r.Score)
                .ToListAsync();

        public async Task<Recommendation?> GetByIdAsync(int id)
            => await _context.Recommendations.FindAsync(id);

        public async Task AddAsync(Recommendation recommendation)
            => await _context.Recommendations.AddAsync(recommendation);

        public async Task MarkAsSeenAsync(int id)
        {
            var recommendation = await _context.Recommendations.FindAsync(id);
            if (recommendation != null)
            {
                recommendation.IsSeen = true;
            }
        }

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}