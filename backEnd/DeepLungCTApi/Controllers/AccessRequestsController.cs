using DeepLungCTApi.Data;
using DeepLungCTApi.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using BCrypt.Net;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api/access-requests")]
public class AccessRequestsController : ControllerBase
{
    private readonly AppDbContext _db;

    public AccessRequestsController(AppDbContext db)
    {
        _db = db;
    }

    // ─── Public: submit a new access request ──────────────────────────────────

    public record SubmitRequest(
        string FirstName,
        string LastName,
        string Personnummer,
        string MobileNumber,
        string Email,
        string Position
    );

    [HttpPost]
    [AllowAnonymous]
    public async Task<IActionResult> Submit([FromBody] SubmitRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.FirstName) ||
            string.IsNullOrWhiteSpace(req.LastName) ||
            string.IsNullOrWhiteSpace(req.Personnummer) ||
            string.IsNullOrWhiteSpace(req.MobileNumber) ||
            string.IsNullOrWhiteSpace(req.Email) ||
            string.IsNullOrWhiteSpace(req.Position))
        {
            return BadRequest(new { detail = "All fields are required." });
        }

        var pnr = req.Personnummer.Replace(" ", "");
        if (pnr.Length != 11 || !pnr.All(char.IsDigit))
            return BadRequest(new { detail = "Personnummer must be exactly 11 digits." });

        var ar = new AccessRequest
        {
            FirstName = req.FirstName.Trim(),
            LastName = req.LastName.Trim(),
            Personnummer = pnr,
            MobileNumber = req.MobileNumber.Trim(),
            Email = req.Email.Trim().ToLowerInvariant(),
            Position = req.Position.Trim(),
            Status = "pending",
            SubmittedAtUtc = DateTime.UtcNow,
        };

        _db.AccessRequests.Add(ar);
        await _db.SaveChangesAsync();
        return Ok(new { ar.Id });
    }

    // ─── Admin: list all access requests ─────────────────────────────────────

    [HttpGet]
    [Authorize(Roles = "admin")]
    public async Task<IActionResult> GetAll()
    {
        var list = await _db.AccessRequests
            .OrderByDescending(r => r.SubmittedAtUtc)
            .Select(r => new
            {
                r.Id,
                r.FirstName,
                r.LastName,
                r.Personnummer,
                r.MobileNumber,
                r.Email,
                r.Position,
                r.Status,
                submittedAt = r.SubmittedAtUtc.ToString("o"),
            })
            .ToListAsync();

        return Ok(list);
    }

    // ─── Admin: approve and create user account ───────────────────────────────

    public record ApproveRequest(string UserId, string TempPassword);

    [HttpPost("{id:int}/approve")]
    [Authorize(Roles = "admin")]
    public async Task<IActionResult> Approve(int id, [FromBody] ApproveRequest req)
    {
        var ar = await _db.AccessRequests.FindAsync(id);
        if (ar is null) return NotFound(new { detail = "Request not found." });
        if (ar.Status != "pending")
            return Conflict(new { detail = "Request has already been handled." });

        if (string.IsNullOrWhiteSpace(req.UserId) || string.IsNullOrWhiteSpace(req.TempPassword))
            return BadRequest(new { detail = "UserId and TempPassword are required." });

        var userId = req.UserId.Trim().ToLowerInvariant();

        // Ensure UserId is unique
        if (await _db.Users.AnyAsync(u => u.UserId == userId))
            return Conflict(new { detail = $"UserId '{userId}' is already taken." });

        // Ensure email is unique
        if (await _db.Users.AnyAsync(u => u.Email == ar.Email))
            return Conflict(new { detail = $"A user with email '{ar.Email}' already exists." });

        var user = new User
        {
            UserId = userId,
            Email = ar.Email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.TempPassword),
            Role = "doctor",
            FirstName = ar.FirstName,
            LastName = ar.LastName,
            Position = ar.Position,
            MobileNumber = ar.MobileNumber,
            MustChangePassword = true,
            CreatedAtUtc = DateTime.UtcNow,
        };

        _db.Users.Add(user);
        ar.Status = "approved";
        await _db.SaveChangesAsync();

        return Ok(new { userId, email = ar.Email });
    }

    // ─── Admin: reject a request ──────────────────────────────────────────────

    [HttpPost("{id:int}/reject")]
    [Authorize(Roles = "admin")]
    public async Task<IActionResult> Reject(int id)
    {
        var ar = await _db.AccessRequests.FindAsync(id);
        if (ar is null) return NotFound(new { detail = "Request not found." });
        if (ar.Status != "pending")
            return Conflict(new { detail = "Request has already been handled." });

        ar.Status = "rejected";
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
