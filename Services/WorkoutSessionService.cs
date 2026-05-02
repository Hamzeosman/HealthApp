using HealthApp.API.DTOs;
using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class WorkoutSessionService : IWorkoutSessionService
    {
        private readonly IWorkoutSessionRepository _repository;

        public WorkoutSessionService(IWorkoutSessionRepository repository)
        {
            _repository = repository;
        }

        public async Task<IEnumerable<WorkoutSessionDto>> GetByUserIdAsync(int userId)
        {
            var sessions = await _repository.GetByUserIdAsync(userId);
            return sessions.Select(MapToDto);
        }

        public async Task<WorkoutSessionDto?> GetByIdAsync(int id)
        {
            var session = await _repository.GetByIdAsync(id);
            return session == null ? null : MapToDto(session);
        }

        public async Task<WorkoutSessionDto> AddWorkoutSessionAsync(CreateWorkoutSessionDto dto)
        {
           var session = new WorkoutSession
{
                UserId = dto.UserId,
                TemplateId = dto.TemplateId,
                Date = DateTime.SpecifyKind(dto.Date, DateTimeKind.Utc),
                StartTime = dto.StartTime.HasValue ? DateTime.SpecifyKind(dto.StartTime.Value, DateTimeKind.Utc) : null,
                EndTime = dto.EndTime.HasValue ? DateTime.SpecifyKind(dto.EndTime.Value, DateTimeKind.Utc) : null,
                DurationMinutes = dto.DurationMinutes,
                TotalCalories = dto.TotalCalories,
                Mood = dto.Mood,
                Notes = dto.Notes,
                WorkoutExercises = dto.WorkoutExercises.Select(we => new WorkoutExercise
                {
                    ExerciseId = we.ExerciseId,
                    Sets = we.Sets,
                    Reps = we.Reps,
                    WeightKg = we.WeightKg,
                    DurationSeconds = we.DurationSeconds,
                    RestSeconds = we.RestSeconds,
                    Rpe = we.Rpe,
                    Notes = we.Notes
                }).ToList()
            };

            await _repository.AddAsync(session);
            await _repository.SaveChangesAsync();

            return MapToDto(session);
        }

        private static WorkoutSessionDto MapToDto(WorkoutSession session) => new()
        {
            Id = session.Id,
            UserId = session.UserId,
            Date = session.Date,
            StartTime = session.StartTime,
            EndTime = session.EndTime,
            DurationMinutes = session.DurationMinutes,
            TotalCalories = session.TotalCalories,
            Mood = session.Mood,
            Notes = session.Notes,
            WorkoutExercises = session.WorkoutExercises.Select(we => new WorkoutExerciseDto
            {
                Id = we.Id,
                ExerciseId = we.ExerciseId,
                ExerciseName = we.Exercise?.Name ?? string.Empty,
                Sets = we.Sets,
                Reps = we.Reps,
                WeightKg = we.WeightKg,
                DurationSeconds = we.DurationSeconds,
                Rpe = we.Rpe,
                Notes = we.Notes
            }).ToList()
        };
    }
}