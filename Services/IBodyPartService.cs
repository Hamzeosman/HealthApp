using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IBodyPartService
    {
        Task<IEnumerable<BodyPart>> GetAllAsync();
        Task<BodyPart?> GetByIdAsync(int id);
        Task AddAsync(BodyPart bodyPart);
    }
}