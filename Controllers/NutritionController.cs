using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Helpers;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class NutritionController : ControllerBase
    {
        private readonly DataDbContext _context;

        public NutritionController(DataDbContext context)
        {
            _context = context;
        }

        [HttpGet("meals")]
        public async Task<IActionResult> GetMeals()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var meals = await (from m in _context.MealLogs
                               join f in _context.Foods on m.FoodId equals f.Id
                               where m.UserId == userId
                               orderby m.Date descending
                               select new
                               {
                                   m.Id,
                                   m.Date,
                                   m.MealType,
                                   FoodName = f.Name,
                                   m.AmountG,
                                   m.Calories,
                                   m.ProteinG,
                                   m.CarbsG,
                                   m.FatG
                               }).ToListAsync();
            return Ok(meals);
        }

        [HttpGet("foods")]
        public async Task<IActionResult> GetFoods()
        {
            var foods = await _context.Foods
                .OrderBy(f => f.Name)
                .ToListAsync();
            return Ok(foods);
        }
    }
}