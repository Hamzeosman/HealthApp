using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IEquipmentService
    {
        Task<IEnumerable<Equipment>> GetAllAsync();
        Task<Equipment?> GetByIdAsync(int id);
        Task AddAsync(Equipment equipment);
    }
}