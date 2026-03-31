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

    // ─── GET /api/admin/stats ─────────────────────────────────────────────────

    [HttpGet("stats")]
    public async Task<IActionResult> GetStats([FromQuery] DateTime? from, [FromQuery] DateTime? to)
    {
        var since  = from?.ToUniversalTime() ?? DateTime.UtcNow.AddDays(-30);
        var before = (to?.ToUniversalTime() ?? DateTime.UtcNow).Date.AddDays(1); // inclusive of 'to' day

        var results = await _db.AnalysisResults
            .Where(r => r.CreatedAtUtc >= since && r.CreatedAtUtc < before)
            .Select(r => new { r.Prediction, r.CreatedAtUtc })
            .ToListAsync();

        var daily = results
            .GroupBy(r => r.CreatedAtUtc.Date)
            .OrderBy(g => g.Key)
            .Select(g => new
            {
                date      = g.Key.ToString("yyyy-MM-dd"),
                benign    = g.Count(r => r.Prediction == "Benign"),
                malignant = g.Count(r => r.Prediction == "Malignancy"),
                total     = g.Count(),
            })
            .ToList();

        return Ok(new
        {
            from      = since.ToString("yyyy-MM-dd"),
            total     = results.Count,
            benign    = results.Count(r => r.Prediction == "Benign"),
            malignant = results.Count(r => r.Prediction == "Malignancy"),
            daily,
        });
    }

    // ─── GET /api/admin/logs ──────────────────────────────────────────────────

    [HttpGet("logs")]
    public async Task<IActionResult> GetLogs([FromQuery] int limit = 100)
    {
        if (limit < 1) limit = 1;
        if (limit > 500) limit = 500;

        var logs = await _db.AnalysisResults
            .Include(r => r.User)
            .OrderByDescending(r => r.CreatedAtUtc)
            .Take(limit)
            .Select(r => new
            {
                r.Id,
                userId = r.User != null ? r.User.UserId : "—",
                r.UserEmail,
                r.Filename,
                r.Prediction,
                r.Confidence,
                r.SizeBytes,
                createdAt = r.CreatedAtUtc.ToString("o"),
            })
            .ToListAsync();

        return Ok(logs);
    }

    // ─── GET /api/admin/health ────────────────────────────────────────────────

    [HttpGet("health")]
    public async Task<IActionResult> GetHealth()
    {
        var totalUsers = await _db.Users.CountAsync();
        var totalAnalyses = await _db.AnalysisResults.CountAsync();
        var pendingRequests = await _db.AccessRequests.CountAsync(r => r.Status == "pending");

        string pythonStatus = "unknown";
        try
        {
            using var http = new System.Net.Http.HttpClient { Timeout = TimeSpan.FromSeconds(3) };
            var resp = await http.GetAsync("http://127.0.0.1:8001/health");
            pythonStatus = resp.IsSuccessStatusCode ? "online" : "error";
        }
        catch
        {
            pythonStatus = "offline";
        }

        return Ok(new
        {
            apiStatus = "online",
            pythonServiceStatus = pythonStatus,
            totalUsers,
            totalAnalyses,
            pendingRequests,
            checkedAt = DateTime.UtcNow.ToString("o"),
        });
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
