using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IBodyPartService
    {
        Task<IEnumerable<BodyPart>> GetAllAsync();
        Task<BodyPart?> GetByIdAsync(int id);
        Task AddAsync(BodyPart bodyPart);
    }
}