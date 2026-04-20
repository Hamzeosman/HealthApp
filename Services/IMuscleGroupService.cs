using HealthApp.API.Models;

namespace HealthApp.API.Services
{
    public interface IMuscleGroupService
    {
        Task<IEnumerable<MuscleGroup>> GetAllAsync();
        Task<IEnumerable<MuscleGroup>> GetByBodyPartIdAsync(int bodyPartId);
        Task<MuscleGroup?> GetByIdAsync(int id);
        Task AddAsync(MuscleGroup muscleGroup);
    }
}