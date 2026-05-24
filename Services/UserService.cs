using HealthApp.API.DTOs;
using HealthApp.API.Models;
using HealthApp.API.Repositories;

namespace HealthApp.API.Services
{
    public class UserService : IUserService
    {
        private readonly IUserRepository _userRepository;

        public UserService(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        public async Task<UserProfileDto?> GetProfileAsync(int userId)
        {
            var user = await _userRepository.GetByIdAsync(userId);
            return user == null ? null : ToProfileDto(user);
        }

        public async Task<UserProfileDto?> UpdateProfileAsync(int userId, UpdateProfileDto dto)
        {
            var user = await _userRepository.GetByIdAsync(userId);
            if (user == null) return null;

            // Endast uppdatera fält som faktiskt skickats in (partial update)
            if (dto.Age.HasValue) user.Age = dto.Age.Value;
            if (dto.WeightKg.HasValue) user.WeightKg = dto.WeightKg.Value;
            if (dto.HeightCm.HasValue) user.HeightCm = dto.HeightCm.Value;
            if (!string.IsNullOrWhiteSpace(dto.FitnessLevel)) user.FitnessLevel = dto.FitnessLevel;
            if (!string.IsNullOrWhiteSpace(dto.Goal)) user.Goal = dto.Goal;

            await _userRepository.SaveChangesAsync();

            return ToProfileDto(user);
        }

        private static UserProfileDto ToProfileDto(User user) => new()
        {
            Name = user.Name,
            Email = user.Email,
            Age = user.Age,
            WeightKg = user.WeightKg,
            HeightCm = user.HeightCm,
            FitnessLevel = user.FitnessLevel,
            Goal = user.Goal,
            CreatedAt = user.CreatedAt
        };
    }
}