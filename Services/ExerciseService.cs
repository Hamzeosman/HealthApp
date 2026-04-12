using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class ExerciseService : IExerciseService
    {
        private readonly IExerciseRepository _repository;

        public ExerciseService(IExerciseRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<Exercise>> GetAllExercisesAsync()
            => await _repository.GetAllAsync();

        public async Task<IEnumerable<Exercise>> GetByMuscleGroupAsync(string muscleGroup)
            => await _repository.GetByMuscleGroupAsync(muscleGroup);

        public async Task<Exercise?> GetByIdAsync(int id)
            => await _repository.GetByIdAsync(id);

        public async Task AddExerciseAsync(Exercise exercise)
        {
            await _repository.AddAsync(exercise);
            await _repository.SaveChangesAsync();
        }
    }
}