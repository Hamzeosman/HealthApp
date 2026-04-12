using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<User> Users { get; set; }
        public DbSet<Exercise> Exercises { get; set; }
        public DbSet<WorkoutSession> WorkoutSessions { get; set; }
        public DbSet<WorkoutExercise> WorkoutExercises { get; set; }
    }
}