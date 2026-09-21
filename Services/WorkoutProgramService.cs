using Mintakt.API.Models;
using Mintakt.API.Repositories;

namespace Mintakt.API.Services
{
    public class WorkoutProgramService : IWorkoutProgramService
    {
        private readonly IWorkoutProgramRepository _repository;

        public WorkoutProgramService(IWorkoutProgramRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<WorkoutProgram>> GetAllAsync()
            => await _repository.GetAllAsync();

        public async Task<WorkoutProgram?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddAsync(WorkoutProgram program)
        {
            await _repository.AddAsync(program);
            await _repository.SaveChangesAsync();
        }
    }
}