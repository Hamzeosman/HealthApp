using Mintakt.API.DTOs;
using Mintakt.API.Models;
using Mintakt.API.Repositories;

namespace Mintakt.API.Services
{
    /// <summary>
    /// Service för träningspass. Mappar mellan API-DTOs (WorkoutSessionDto,
    /// CreateWorkoutSessionDto) och persistens-modellen WorkoutSessionData
    /// som lever i DataDbContext (HealthAppDataDb, snake_case).
    ///
    /// Issue #68 / Issue #32: tidigare mappades DTOs till den gamla WorkoutSession-modellen
    /// mot AppDbContext. Nu används WorkoutSessionData så att POST och GET pratar med
    /// samma DB (HealthAppDataDb) och Python-pipelinen ser datan.
    /// </summary>
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
            var session = new WorkoutSessionData
            {
                UserId = dto.UserId,
                TemplateId = dto.TemplateId,
                Date = DateTime.SpecifyKind(dto.Date, DateTimeKind.Utc),
                StartTime = dto.StartTime.HasValue
                    ? DateTime.SpecifyKind(dto.StartTime.Value, DateTimeKind.Utc)
                    : null,
                EndTime = dto.EndTime.HasValue
                    ? DateTime.SpecifyKind(dto.EndTime.Value, DateTimeKind.Utc)
                    : null,
                DurationMinutes = dto.DurationMinutes,
                TotalCalories = dto.TotalCalories,
                // Tom sträng bryter mot CHECK-constrainten, medan NULL är tillåtet.
                Mood = string.IsNullOrWhiteSpace(dto.Mood) ? null : dto.Mood,
                Notes = dto.Notes,
                CreatedAt = DateTime.UtcNow,
                WorkoutExercises = dto.WorkoutExercises.Select(we => new WorkoutExerciseData
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

        private static WorkoutSessionDto MapToDto(WorkoutSessionData session) => new()
        {
            Id = session.Id,
            UserId = session.UserId ?? 0,
            Date = session.Date ?? DateTime.MinValue,
            StartTime = session.StartTime,
            EndTime = session.EndTime,
            DurationMinutes = session.DurationMinutes,
            TotalCalories = session.TotalCalories,
            Mood = session.Mood ?? string.Empty,
            Notes = session.Notes ?? string.Empty,
            WorkoutExercises = session.WorkoutExercises.Select(we => new WorkoutExerciseDto
            {
                Id = we.Id,
                ExerciseId = we.ExerciseId ?? 0,
                ExerciseName = we.Exercise?.Name ?? string.Empty,
                Sets = we.Sets ?? 0,
                Reps = we.Reps ?? 0,
                WeightKg = we.WeightKg,
                DurationSeconds = we.DurationSeconds,
                Rpe = we.Rpe,
                Notes = we.Notes ?? string.Empty
            }).ToList()
        };
    }
}