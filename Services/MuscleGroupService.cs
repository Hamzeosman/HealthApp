using Mintakt.API.Models;
using Mintakt.API.Repositories;

namespace Mintakt.API.Services
{
    public class MuscleGroupService : IMuscleGroupService
    {
        private readonly IMuscleGroupRepository _repository;

        public MuscleGroupService(IMuscleGroupRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<MuscleGroup>> GetAllAsync()
            => await _repository.GetAllAsync();

        public async Task<IEnumerable<MuscleGroup>> GetByBodyPartIdAsync(int bodyPartId)
            => await _repository.GetByBodyPartIdAsync(bodyPartId);

        public async Task<MuscleGroup?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(MuscleGroup muscleGroup)
        {
            await _repository.AddAsync(muscleGroup);
            await _repository.SaveChangesAsync();
        }
    }
}