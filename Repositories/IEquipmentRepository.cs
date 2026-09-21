using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IEquipmentRepository
    {
        Task<IEnumerable<Equipment>> GetAllAsync();
        Task<Equipment?> GetByIdAsync(int id);
        Task AddAsync(Equipment equipment);
        Task SaveChangesAsync();
    }
}