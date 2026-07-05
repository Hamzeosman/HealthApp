using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API
{
    public class DataDbContext : DbContext
    {
        public DataDbContext(DbContextOptions<DataDbContext> options) : base(options) { }

        // Iteration 1 (Issue #32) — new DbSets
        public DbSet<UserData> Users { get; set; }
        public DbSet<EquipmentData> Equipment { get; set; }

        // Existing DbSets
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

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // UserData: check constraints matching schema.sql
            modelBuilder.Entity<UserData>()
                .ToTable("users", t =>
                {
                    t.HasCheckConstraint(
                        "CK_users_fitness_level",
                        "fitness_level IN ('nybörjare','medel','avancerad')");
                    t.HasCheckConstraint(
                        "CK_users_goal",
                        "goal IN ('bygga_muskler','gå_ner_i_vikt','öka_kondition','hålla_sig_i_form')");
                });

            // ExerciseData: check constraints matching schema.sql
            modelBuilder.Entity<ExerciseData>()
                .ToTable("exercises", t =>
                {
                    t.HasCheckConstraint(
                        "CK_exercises_difficulty",
                        "difficulty IN ('nybörjare','medel','avancerad')");
                    t.HasCheckConstraint(
                        "CK_exercises_exercise_type",
                        "exercise_type IN ('styrka','kondition','stretching','balans')");
                });

            // ExerciseData → EquipmentData navigation (foreign key already on entity)
            modelBuilder.Entity<ExerciseData>()
                .HasOne(e => e.Equipment)
                .WithMany()
                .HasForeignKey(e => e.EquipmentId)
                .OnDelete(DeleteBehavior.SetNull);
        }
    }
}