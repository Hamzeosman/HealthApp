using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IPersonalRecordService
    {
        Task<IEnumerable<PersonalRecord>> GetByUserIdAsync(int userId);
        Task<IEnumerable<PersonalRecord>> GetByExerciseIdAsync(int exerciseId);
        Task<PersonalRecord?> GetByIdAsync(int id);
        Task AddAsync(PersonalRecord record);
    }
}