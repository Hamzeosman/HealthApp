using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API
{
    public class DataDbContext : DbContext
    {
        public DataDbContext(DbContextOptions<DataDbContext> options) : base(options) { }

        public DbSet<TrainingPlan> TrainingPlans { get; set; }
        public DbSet<AiInsight> AiInsights { get; set; }
        public DbSet<WorkoutSessionData> WorkoutSessions { get; set; }
        public DbSet<ExerciseData> Exercises { get; set; }
    }
}