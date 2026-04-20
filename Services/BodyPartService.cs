using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class BodyPartService : IBodyPartService
    {
        private readonly IBodyPartRepository _repository;

        public BodyPartService(IBodyPartRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<BodyPart>> GetAllAsync()
            => await _repository.GetAllAsync();

        public async Task<BodyPart?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(BodyPart bodyPart)
        {
            await _repository.AddAsync(bodyPart);
            await _repository.SaveChangesAsync();
        }
    }
}