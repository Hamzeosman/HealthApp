using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class EquipmentController : ControllerBase
    {
        private readonly IEquipmentService _service;

        public EquipmentController(IEquipmentService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var equipments = await _service.GetAllAsync();
            return Ok(equipments);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var equipment = await _service.GetByIdAsync(id);
            if (equipment == null) return NotFound();
            return Ok(equipment);
        }

        [HttpPost]
        public async Task<IActionResult> Add(Equipment equipment)
        {
            await _service.AddAsync(equipment);
            return CreatedAtAction(nameof(GetById), new { id = equipment.Id }, equipment);
        }
    }
}