using Mintakt.API.Models;

namespace Mintakt.API.Repositories
{
    public interface IMuscleGroupRepository
    {
        Task<IEnumerable<MuscleGroup>> GetAllAsync();
        Task<IEnumerable<MuscleGroup>> GetByBodyPartIdAsync(int bodyPartId);
        Task<MuscleGroup?> GetByIdAsync(int id);
        Task AddAsync(MuscleGroup muscleGroup);
        Task SaveChangesAsync();
    }
}