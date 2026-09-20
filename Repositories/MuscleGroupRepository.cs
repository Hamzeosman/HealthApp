using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public class MuscleGroupRepository : IMuscleGroupRepository
    {
        private readonly AppDbContext _context;

        public MuscleGroupRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<MuscleGroup>> GetAllAsync()
            => await _context.MuscleGroups.ToListAsync();

        public async Task<IEnumerable<MuscleGroup>> GetByBodyPartIdAsync(int bodyPartId)
            => await _context.MuscleGroups
                .Where(m => m.BodyPartId == bodyPartId)
                .ToListAsync();

        public async Task<MuscleGroup?> GetByIdAsync(int id)
            => await _context.MuscleGroups.FindAsync(id);

        public async Task AddAsync(MuscleGroup muscleGroup)
            => await _context.MuscleGroups.AddAsync(muscleGroup);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}