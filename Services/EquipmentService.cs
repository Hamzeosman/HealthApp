using Mintakt.API.Models;
using Mintakt.API.Repositories;

namespace Mintakt.API.Services
{
    public class EquipmentService : IEquipmentService
    {
        private readonly IEquipmentRepository _repository;

        public EquipmentService(IEquipmentRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<Equipment>> GetAllAsync()
            => await _repository.GetAllAsync();

        public async Task<Equipment?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(Equipment equipment)
        {
            await _repository.AddAsync(equipment);
            await _repository.SaveChangesAsync();
        }
    }
}