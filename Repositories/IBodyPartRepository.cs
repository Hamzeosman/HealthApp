using HealthApp.API.Models;

namespace HealthApp.API.Repositories
{
    public interface IBodyPartRepository
    {
        Task<IEnumerable<BodyPart>> GetAllAsync();
        Task<BodyPart?> GetByIdAsync(int id);
        Task AddAsync(BodyPart bodyPart);
        Task SaveChangesAsync();
    }
}