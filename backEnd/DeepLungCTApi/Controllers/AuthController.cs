using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using DeepLungCTApi.Data;
using DeepLungCTApi.Dtos;
using DeepLungCTApi.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
public class AuthController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IConfiguration _cfg;

    public AuthController(AppDbContext db, IConfiguration cfg)
    {
        _db = db;
        _cfg = cfg;
    }

    [HttpPost("register")]
    public async Task<ActionResult<AuthResponse>> Register([FromBody] RegisterRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) ||
            string.IsNullOrWhiteSpace(req.Password) ||
            string.IsNullOrWhiteSpace(req.ConfirmPassword))
        {
            return BadRequest(new { detail = "Please fill in all fields." });
        }

        if (req.Password != req.ConfirmPassword)
            return BadRequest(new { detail = "Passwords do not match." });

        var role = (req.Role ?? "doctor").Trim().ToLowerInvariant();
        if (role != "doctor" && role != "admin")
            role = "doctor";

        var email = req.Email.Trim().ToLowerInvariant();

        if (await _db.Users.AnyAsync(u => u.Email == email))
            return Conflict(new { detail = "An account with this email already exists." });

        var user = new User
        {
            Email = email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(req.Password),
            Role = role,
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync();

        return Ok(new AuthResponse
        {
            Email = user.Email,
            Role = user.Role,
            Token = BuildJwt(user),
        });
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login([FromBody] LoginRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) || string.IsNullOrWhiteSpace(req.Password))
            return BadRequest(new { detail = "Please enter email and password." });

        var email = req.Email.Trim().ToLowerInvariant();
        var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == email);

        if (user == null || !BCrypt.Net.BCrypt.Verify(req.Password, user.PasswordHash))
            return Unauthorized(new { detail = "Invalid email or password." });

        return Ok(new AuthResponse
        {
            Email = user.Email,
            Role = user.Role,
            Token = BuildJwt(user),
        });
    }

    private string BuildJwt(User user)
    {
        var secret = _cfg["Jwt:Secret"]!;
        var issuer = _cfg["Jwt:Issuer"]!;
        var audience = _cfg["Jwt:Audience"]!;
        var hours = int.TryParse(_cfg["Jwt:ExpiresHours"], out var h) ? h : 24;

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.Role, user.Role),
            new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new Claim(JwtRegisteredClaimNames.Email, user.Email),
        };

        var token = new JwtSecurityToken(
            issuer: issuer,
            audience: audience,
            claims: claims,
            expires: DateTime.UtcNow.AddHours(hours),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}