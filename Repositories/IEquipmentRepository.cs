using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IEquipmentRepository
    {
        Task<IEnumerable<Equipment>> GetAllAsync();
        Task<Equipment?> GetByIdAsync(int id);
        Task AddAsync(Equipment equipment);
        Task SaveChangesAsync();
    }
}