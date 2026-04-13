using Microsoft.AspNetCore.Mvc;
using HealthApp.API.DTOs;
using HealthApp.API.Services;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;

        public AuthController(IAuthService authService)
        {
            _authService = authService;
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register(RegisterDto dto)
        {
            var token = await _authService.RegisterAsync(dto);
            if (token == null) return BadRequest("Användarnamnet är redan taget.");
            return Ok(new { token });
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login(LoginDto dto)
        {
            var token = await _authService.LoginAsync(dto);
            if (token == null) return Unauthorized("Fel användarnamn eller lösenord.");
            return Ok(new { token });
        }
    }
}