using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public class EquipmentRepository : IEquipmentRepository
    {
        private readonly AppDbContext _context;

        public EquipmentRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Equipment>> GetAllAsync()
            => await _context.Equipments.ToListAsync();

        public async Task<Equipment?> GetByIdAsync(int id)
            => await _context.Equipments.FindAsync(id);

        public async Task AddAsync(Equipment equipment)
            => await _context.Equipments.AddAsync(equipment);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}