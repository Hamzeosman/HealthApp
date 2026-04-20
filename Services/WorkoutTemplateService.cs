using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class WorkoutTemplateService : IWorkoutTemplateService
    {
        private readonly IWorkoutTemplateRepository _repository;

        public WorkoutTemplateService(IWorkoutTemplateRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<WorkoutTemplate>> GetByProgramIdAsync(int programId)
            => await _repository.GetByProgramIdAsync(programId);

        public async Task<WorkoutTemplate?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(WorkoutTemplate template)
        {
            await _repository.AddAsync(template);
            await _repository.SaveChangesAsync();
        }
    }
}