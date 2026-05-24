using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using HealthApp.API.DTOs;
using HealthApp.API.Helpers;
using HealthApp.API.Services;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class UserController : ControllerBase
    {
        private readonly IUserService _userService;

        public UserController(IUserService userService)
        {
            _userService = userService;
        }

        [HttpGet("me")]
        public async Task<IActionResult> GetMyProfile()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var profile = await _userService.GetProfileAsync(userId.Value);
            if (profile == null) return NotFound();

            return Ok(profile);
        }

        [HttpPut("me")]
        public async Task<IActionResult> UpdateMyProfile(UpdateProfileDto dto)
        {
            if (!ModelState.IsValid) return BadRequest(ModelState);

            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var updated = await _userService.UpdateProfileAsync(userId.Value, dto);
            if (updated == null) return NotFound();

            return Ok(updated);
        }
    }
}