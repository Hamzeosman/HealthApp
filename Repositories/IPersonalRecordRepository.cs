using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IPersonalRecordRepository
    {
        Task<IEnumerable<PersonalRecord>> GetByUserIdAsync(int userId);
        Task<IEnumerable<PersonalRecord>> GetByExerciseIdAsync(int exerciseId);
        Task<PersonalRecord?> GetByIdAsync(int id);
        Task AddAsync(PersonalRecord record);
        Task SaveChangesAsync();
    }
}