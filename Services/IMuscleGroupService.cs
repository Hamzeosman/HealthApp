using Mintakt.API.Models;

namespace Mintakt.API.Services
{
    public interface IMuscleGroupService
    {
        Task<IEnumerable<MuscleGroup>> GetAllAsync();
        Task<IEnumerable<MuscleGroup>> GetByBodyPartIdAsync(int bodyPartId);
        Task<MuscleGroup?> GetByIdAsync(int id);
        Task AddAsync(MuscleGroup muscleGroup);
    }
}