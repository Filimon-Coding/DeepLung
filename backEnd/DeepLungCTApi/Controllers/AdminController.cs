using DeepLungCTApi.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api/admin")]
[Authorize(Roles = "admin")]
public class AdminController : ControllerBase
{
    private readonly AppDbContext _db;

    public AdminController(AppDbContext db) => _db = db;

    // ─── GET /api/admin/users ─────────────────────────────────────────────────

    [HttpGet("users")]
    public async Task<IActionResult> ListUsers()
    {
        var users = await _db.Users
            .OrderBy(u => u.LastName)
            .ThenBy(u => u.FirstName)
            .Select(u => new
            {
                u.Id,
                u.UserId,
                u.FirstName,
                u.LastName,
                u.Email,
                u.MobileNumber,
                u.Position,
                u.Role,
                u.MustChangePassword,
                createdAt = u.CreatedAtUtc.ToString("o"),
            })
            .ToListAsync();

        return Ok(users);
    }

    // ─── PUT /api/admin/users/{id} ────────────────────────────────────────────

    public record UpdateUserRequest(
        string? FirstName,
        string? LastName,
        string? Email,
        string? MobileNumber,
        string? Position,
        string? Role
    );

    [HttpPut("users/{id:int}")]
    public async Task<IActionResult> UpdateUser(int id, [FromBody] UpdateUserRequest req)
    {
        var user = await _db.Users.FindAsync(id);
        if (user is null) return NotFound(new { detail = "User not found." });

        if (!string.IsNullOrWhiteSpace(req.FirstName))
            user.FirstName = req.FirstName.Trim();

        if (!string.IsNullOrWhiteSpace(req.LastName))
            user.LastName = req.LastName.Trim();

        if (!string.IsNullOrWhiteSpace(req.Email))
        {
            var email = req.Email.Trim().ToLowerInvariant();
            if (await _db.Users.AnyAsync(u => u.Email == email && u.Id != id))
                return Conflict(new { detail = "Email already in use." });
            user.Email = email;
        }

        if (!string.IsNullOrWhiteSpace(req.MobileNumber))
            user.MobileNumber = req.MobileNumber.Trim();

        if (!string.IsNullOrWhiteSpace(req.Position))
            user.Position = req.Position.Trim();

        if (!string.IsNullOrWhiteSpace(req.Role))
        {
            var role = req.Role.Trim().ToLowerInvariant();
            if (role != "doctor" && role != "admin") role = "doctor";
            user.Role = role;
        }

        await _db.SaveChangesAsync();
        return Ok(new { user.Id, user.UserId, user.FirstName, user.LastName, user.Email, user.Role });
    }

    // ─── DELETE /api/admin/users/{id} ─────────────────────────────────────────

    [HttpDelete("users/{id:int}")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        var user = await _db.Users.FindAsync(id);
        if (user is null) return NotFound(new { detail = "User not found." });

        if (user.Role == "admin")
        {
            var adminCount = await _db.Users.CountAsync(u => u.Role == "admin");
            if (adminCount <= 1)
                return Conflict(new { detail = "Cannot delete the last admin account." });
        }

        _db.Users.Remove(user);
        await _db.SaveChangesAsync();
        return NoContent();
    }

    // ─── POST /api/admin/users/{id}/reset-password ────────────────────────────

    public record ResetPasswordRequest(string NewPassword);

    [HttpPost("users/{id:int}/reset-password")]
    public async Task<IActionResult> ResetPassword(int id, [FromBody] ResetPasswordRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.NewPassword) || req.NewPassword.Length < 8)
            return BadRequest(new { detail = "Password must be at least 8 characters." });

        var user = await _db.Users.FindAsync(id);
        if (user is null) return NotFound(new { detail = "User not found." });

        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.NewPassword);
        user.MustChangePassword = true;
        await _db.SaveChangesAsync();

        return Ok(new { detail = "Password reset. User must change it on next login." });
    }
}
