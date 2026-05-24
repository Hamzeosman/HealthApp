using HealthApp.API.DTOs;
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
            if (user == null) return null;

            return new UserProfileDto
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

        public async Task<UserProfileDto?> UpdateProfileAsync(int userId, UpdateProfileDto dto)
        {
            var user = await _userRepository.GetByIdAsync(userId);
            if (user == null) return null;

            user.Age = dto.Age;
            user.WeightKg = dto.WeightKg;
            user.HeightCm = dto.HeightCm;
            user.FitnessLevel = dto.FitnessLevel;
            user.Goal = dto.Goal;

            await _userRepository.SaveChangesAsync();

            return new UserProfileDto
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
}
