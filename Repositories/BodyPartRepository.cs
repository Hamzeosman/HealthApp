using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class BodyPartRepository : IBodyPartRepository
    {
        private readonly AppDbContext _context;

        public BodyPartRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<BodyPart>> GetAllAsync()
            => await _context.BodyParts.ToListAsync();

        public async Task<BodyPart?> GetByIdAsync(int id)
            => await _context.BodyParts.FindAsync(id);

        public async Task AddAsync(BodyPart bodyPart)
            => await _context.BodyParts.AddAsync(bodyPart);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}