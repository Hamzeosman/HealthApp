using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API
{
    public class DataDbContext : DbContext
    {
        public DataDbContext(DbContextOptions<DataDbContext> options) : base(options) { }

        // Iteration 1 (Issue #32) — new DbSets
        public DbSet<UserData> Users { get; set; }
        public DbSet<EquipmentData> Equipment { get; set; }

        // Iteration 2 (Issue #32) — new DbSets
        public DbSet<WorkoutExerciseData> WorkoutExercises { get; set; }
        public DbSet<PersonalRecordData> PersonalRecords { get; set; }

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

            // ── Iteration 1 (Issue #32) ─────────────────────────────────

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

            // ExerciseData → EquipmentData navigation
            modelBuilder.Entity<ExerciseData>()
                .HasOne(e => e.Equipment)
                .WithMany()
                .HasForeignKey(e => e.EquipmentId)
                .OnDelete(DeleteBehavior.SetNull);

            // ── Iteration 2 (Issue #32) ─────────────────────────────────

            // WorkoutSessionData: check constraint on mood (from schema.sql)
            modelBuilder.Entity<WorkoutSessionData>()
                .ToTable("workout_sessions", t =>
                {
                    t.HasCheckConstraint(
                        "CK_workout_sessions_mood",
                        "mood IN ('bra','okej','trött','stark')");
                });

            // WorkoutSessionData → UserData navigation
            modelBuilder.Entity<WorkoutSessionData>()
                .HasOne(s => s.User)
                .WithMany()
                .HasForeignKey(s => s.UserId)
                .OnDelete(DeleteBehavior.SetNull);

            // WorkoutSessionData → WorkoutExerciseData (one-to-many)
            modelBuilder.Entity<WorkoutSessionData>()
                .HasMany(s => s.WorkoutExercises)
                .WithOne(we => we.Session)
                .HasForeignKey(we => we.SessionId)
                .OnDelete(DeleteBehavior.SetNull);

            // WorkoutExerciseData: check constraints matching migration_p5_quality.sql
            modelBuilder.Entity<WorkoutExerciseData>()
                .ToTable("workout_exercises", t =>
                {
                    t.HasCheckConstraint(
                        "CK_workout_exercises_sets",
                        "sets > 0 AND sets <= 20");
                    t.HasCheckConstraint(
                        "CK_workout_exercises_reps",
                        "reps > 0 AND reps <= 100");
                    t.HasCheckConstraint(
                        "CK_workout_exercises_weight_kg",
                        "weight_kg >= 0 AND weight_kg <= 500");
                    t.HasCheckConstraint(
                        "CK_workout_exercises_rpe",
                        "rpe >= 1 AND rpe <= 10");
                });

            // WorkoutExerciseData → ExerciseData navigation
            modelBuilder.Entity<WorkoutExerciseData>()
                .HasOne(we => we.Exercise)
                .WithMany()
                .HasForeignKey(we => we.ExerciseId)
                .OnDelete(DeleteBehavior.SetNull);

            // PersonalRecordData → UserData navigation
            modelBuilder.Entity<PersonalRecordData>()
                .HasOne(pr => pr.User)
                .WithMany()
                .HasForeignKey(pr => pr.UserId)
                .OnDelete(DeleteBehavior.SetNull);

            // PersonalRecordData → ExerciseData navigation
            modelBuilder.Entity<PersonalRecordData>()
                .HasOne(pr => pr.Exercise)
                .WithMany()
                .HasForeignKey(pr => pr.ExerciseId)
                .OnDelete(DeleteBehavior.SetNull);
        }
    }
}