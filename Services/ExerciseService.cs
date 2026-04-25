using HealthApp.API.DTOs;
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

        public async Task<IEnumerable<ExerciseDto>> GetAllExercisesAsync()
        {
            var exercises = await _repository.GetAllAsync();
            return exercises.Select(MapToDto);
        }

        public async Task<IEnumerable<ExerciseDto>> GetByMuscleGroupAsync(string muscleGroup)
        {
            var exercises = await _repository.GetByMuscleGroupAsync(muscleGroup);
            return exercises.Select(MapToDto);
        }

        public async Task<ExerciseDto?> GetByIdAsync(int id)
        {
            var exercise = await _repository.GetByIdAsync(id);
            return exercise == null ? null : MapToDto(exercise);
        }

        public async Task<ExerciseDto> AddExerciseAsync(CreateExerciseDto dto)
        {
            var exercise = new Exercise
            {
                Name = dto.Name,
                Description = dto.Description,
                BodyPartId = dto.BodyPartId,
                MuscleGroupId = dto.MuscleGroupId,
                EquipmentId = dto.EquipmentId,
                Difficulty = dto.Difficulty,
                ExerciseType = dto.ExerciseType,
                Instructions = dto.Instructions,
                Tips = dto.Tips,
                CaloriesPerMinute = dto.CaloriesPerMinute
            };

            await _repository.AddAsync(exercise);
            await _repository.SaveChangesAsync();

            return MapToDto(exercise);
        }

        private static ExerciseDto MapToDto(Exercise exercise) => new()
        {
            Id = exercise.Id,
            Name = exercise.Name,
            Description = exercise.Description,
            Difficulty = exercise.Difficulty,
            ExerciseType = exercise.ExerciseType,
            Instructions = exercise.Instructions,
            Tips = exercise.Tips,
            CaloriesPerMinute = exercise.CaloriesPerMinute,
            BodyPartName = exercise.BodyPart?.Name,
            MuscleGroupName = exercise.MuscleGroup?.Name,
            EquipmentName = exercise.Equipment?.Name
        };
    }
}