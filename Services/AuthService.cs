using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using Mintakt.API.DTOs;
using Mintakt.API.Models;
using Mintakt.API.Repositories;

namespace Mintakt.API.Services
{
    public class AuthService : IAuthService
    {
        private readonly IUserRepository _userRepository;
        private readonly DataDbContext _dataDb;
        private readonly IConfiguration _configuration;

        public AuthService(
            IUserRepository userRepository,
            DataDbContext dataDb,
            IConfiguration configuration)
        {
            _userRepository = userRepository;
            _dataDb = dataDb;
            _configuration = configuration;
        }

        public async Task<string?> RegisterAsync(RegisterDto dto)
        {
            var existingUser = await _userRepository.GetByUsernameAsync(dto.Username);
            if (existingUser != null) return null;

            var user = new User
            {
                Name = dto.Username,
                Email = dto.Email,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(dto.Password)
            };

            await _userRepository.AddAsync(user);
            await _userRepository.SaveChangesAsync();

            // Synkronisera fitness-profilen till DataDbContext med SAMMA ID
            // så att /me-endpoints och all user-relaterad data fungerar korrekt.
            // Email + PasswordHash lagras BARA i AppDbContext (Identity-ansvar).
            await SyncUserToDataDbAsync(user);

            return GenerateToken(user);
        }

        public async Task<string?> LoginAsync(LoginDto dto)
        {
            var user = await _userRepository.GetByUsernameAsync(dto.Username);
            if (user == null) return null;
            if (!BCrypt.Net.BCrypt.Verify(dto.Password, user.PasswordHash)) return null;

            return GenerateToken(user);
        }

        /// <summary>
        /// Skapar fitness-profil-raden i DataDbContext med SAMMA ID som i AppDbContext.
        /// 
        /// Designval: UserData i DataDbContext är en fitness-profil, inte auth-entitet
        /// (email och password_hash tillhör AppDbContext). Default-värden för
        /// FitnessLevel och Goal matchar DataDbContext CHECK-constraints.
        /// Användaren kan uppdatera dessa via Profile-sidan.
        /// 
        /// Idempotent: om användaren redan finns i DataDbContext skipppas insert.
        /// Vid krasch mellan AppDbContext-save och DataDbContext-save får vi en
        /// desync — se Issue #57 för diskussion om transaktion över två databaser.
        /// För nuvarande scope accepterar vi eventual consistency.
        /// </summary>
        private async Task SyncUserToDataDbAsync(User appUser)
        {
            var exists = await _dataDb.Users.FindAsync(appUser.Id);
            if (exists != null) return;

            var dataUser = new UserData
            {
                Id = appUser.Id,
                Name = appUser.Name,
                FitnessLevel = "nybörjare",
                Goal = "hålla_sig_i_form",
                CreatedAt = DateTime.UtcNow
            };

            _dataDb.Users.Add(dataUser);
            await _dataDb.SaveChangesAsync();
        }

        private string GenerateToken(User user)
        {
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(
                _configuration["Jwt:Key"]!));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var claims = new[]
            {
                new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
                new Claim(ClaimTypes.Name, user.Name)
            };

            var token = new JwtSecurityToken(
                issuer: _configuration["Jwt:Issuer"],
                audience: _configuration["Jwt:Audience"],
                claims: claims,
                expires: DateTime.UtcNow.AddDays(7),
                signingCredentials: creds
            );

            return new JwtSecurityTokenHandler().WriteToken(token);
        }
    }
}