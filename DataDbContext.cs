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
        public DbSet<RunningSession> RunningSessions { get; set; }
        public DbSet<TrainingPlanDay> TrainingPlanDays { get; set; }
        public DbSet<Achievement> Achievements { get; set; }
        public DbSet<UserStreak> UserStreaks { get; set; }
        public DbSet<TrainingPlanExercise> TrainingPlanExercises { get; set; }
        public DbSet<Biometric> Biometrics { get; set; }
        public DbSet<BodyMeasurement> BodyMeasurements { get; set; }
        public DbSet<MealLog> MealLogs { get; set; }
        public DbSet<Food> Foods { get; set; }
    }
}