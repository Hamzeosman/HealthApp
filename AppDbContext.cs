using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<User> Users { get; set; }
        public DbSet<Exercise> Exercises { get; set; }
        public DbSet<BodyPart> BodyParts { get; set; }
        public DbSet<MuscleGroup> MuscleGroups { get; set; }
        public DbSet<Equipment> Equipments { get; set; }
        public DbSet<WorkoutProgram> WorkoutPrograms { get; set; }
        public DbSet<WorkoutTemplate> WorkoutTemplates { get; set; }
        public DbSet<TemplateExercise> TemplateExercises { get; set; }
        public DbSet<WorkoutSession> WorkoutSessions { get; set; }
        public DbSet<WorkoutExercise> WorkoutExercises { get; set; }
        public DbSet<UserProgress> UserProgressList { get; set; }
        public DbSet<PersonalRecord> PersonalRecords { get; set; }
        public DbSet<Recommendation> Recommendations { get; set; }
    }
}