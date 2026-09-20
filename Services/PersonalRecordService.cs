using Mintakt.API.Models;
using Mintakt.API.Repositories;

namespace Mintakt.API.Services
{
    public class PersonalRecordService : IPersonalRecordService
    {
        private readonly IPersonalRecordRepository _repository;

        public PersonalRecordService(IPersonalRecordRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<PersonalRecord>> GetByUserIdAsync(int userId)
            => await _repository.GetByUserIdAsync(userId);

        public async Task<IEnumerable<PersonalRecord>> GetByExerciseIdAsync(int exerciseId)
            => await _repository.GetByExerciseIdAsync(exerciseId);

        public async Task<PersonalRecord?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(PersonalRecord record)
        {
            await _repository.AddAsync(record);
            await _repository.SaveChangesAsync();
        }
    }
}