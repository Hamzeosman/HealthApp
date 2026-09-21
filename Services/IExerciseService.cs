using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    public interface IExerciseService
    {
        Task<IEnumerable<ExerciseDto>> GetAllExercisesAsync();
        Task<IEnumerable<ExerciseDto>> GetByMuscleGroupAsync(string muscleGroup);
        Task<ExerciseDto?> GetByIdAsync(int id);
        Task<ExerciseDto> AddExerciseAsync(CreateExerciseDto dto);
    }
}