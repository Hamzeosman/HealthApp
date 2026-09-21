using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IEquipmentService
    {
        Task<IEnumerable<Equipment>> GetAllAsync();
        Task<Equipment?> GetByIdAsync(int id);
        Task AddAsync(Equipment equipment);
    }
}