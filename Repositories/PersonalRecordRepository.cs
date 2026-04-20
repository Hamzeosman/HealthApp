using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public class PersonalRecordRepository : IPersonalRecordRepository
    {
        private readonly AppDbContext _context;

        public PersonalRecordRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<PersonalRecord>> GetByUserIdAsync(int userId)
            => await _context.PersonalRecords
                .Where(p => p.UserId == userId)
                .OrderByDescending(p => p.Date)
                .ToListAsync();

        public async Task<IEnumerable<PersonalRecord>> GetByExerciseIdAsync(int exerciseId)
            => await _context.PersonalRecords
                .Where(p => p.ExerciseId == exerciseId)
                .OrderByDescending(p => p.WeightKg)
                .ToListAsync();

        public async Task<PersonalRecord?> GetByIdAsync(int id)
            => await _context.PersonalRecords.FindAsync(id);

        public async Task AddAsync(PersonalRecord record)
            => await _context.PersonalRecords.AddAsync(record);

        public async Task SaveChangesAsync()
            => await _context.SaveChangesAsync();
    }
}