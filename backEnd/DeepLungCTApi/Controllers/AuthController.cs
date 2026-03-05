using BCrypt.Net;
using DeepLungCTApi.Data;
using DeepLungCTApi.Dtos;
using DeepLungCTApi.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
public class AuthController : ControllerBase
{
    private readonly AppDbContext _db;

    public AuthController(AppDbContext db)
    {
        _db = db;
    }

    [HttpPost("register")]
    public async Task<ActionResult<AuthResponse>> Register([FromBody] RegisterRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) ||
            string.IsNullOrWhiteSpace(req.Password) ||
            string.IsNullOrWhiteSpace(req.ConfirmPassword))
        {
            return BadRequest(new { detail = "Please fill in email and password fields." });
        }

        if (req.Password != req.ConfirmPassword)
            return BadRequest(new { detail = "Passwords do not match." });

        var role = (req.Role ?? "doctor").Trim().ToLowerInvariant();
        if (role != "doctor" && role != "admin")
            role = "doctor";

        var email = req.Email.Trim().ToLowerInvariant();

        var exists = await _db.Users.AnyAsync(u => u.Email == email);
        if (exists)
            return Conflict(new { detail = "User already exists." });

        var user = new User
        {
            Email = email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.Password),
            Role = role
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync();

        return Ok(new AuthResponse { Email = user.Email, Role = user.Role });
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login([FromBody] LoginRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) || string.IsNullOrWhiteSpace(req.Password))
            return BadRequest(new { detail = "Please enter email and password." });

        var email = req.Email.Trim().ToLowerInvariant();

        var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == email);
        if (user == null)
            return Unauthorized(new { detail = "Invalid email or password." });

        var ok = BCrypt.Net.BCrypt.Verify(req.Password, user.PasswordHash);
        if (!ok)
            return Unauthorized(new { detail = "Invalid email or password." });

        return Ok(new AuthResponse { Email = user.Email, Role = user.Role });
    }
}