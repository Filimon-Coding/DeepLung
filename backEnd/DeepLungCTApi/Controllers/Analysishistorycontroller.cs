using System.Security.Claims;
using DeepLungCTApi.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
[Authorize]
public class AnalysisHistoryController : ControllerBase
{
    private readonly AppDbContext _db;

    public AnalysisHistoryController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet("history")]
    public async Task<IActionResult> GetHistory([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var userId = GetUserId();
        if (userId is null)
            return Unauthorized();

        page = Math.Max(page, 1);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var query = _db.AnalysisResults
            .Where(r => r.UserId == userId.Value)
            .OrderByDescending(r => r.CreatedAtUtc);

        var total = await query.CountAsync();

        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(r => new
            {
                r.Id,
                r.Filename,
                r.Prediction,
                r.Confidence,
                r.ProbBenign,
                r.ProbMalignancy,
                r.CreatedAtUtc,
            })
            .ToListAsync();

        return Ok(new
        {
            total,
            page,
            pageSize,
            items
        });
    }

    [HttpGet("history/{id:int}")]
    public async Task<IActionResult> GetDetail(int id)
    {
        var userId = GetUserId();
        if (userId is null)
            return Unauthorized();

        var item = await _db.AnalysisResults
            .FirstOrDefaultAsync(r => r.Id == id && r.UserId == userId.Value);

        if (item == null)
            return NotFound(new { detail = "Result not found." });

        return Ok(new
        {
            item.Id,
            item.Filename,
            item.ContentType,
            item.SizeBytes,
            item.Prediction,
            item.Confidence,
            item.ProbBenign,
            item.ProbMalignancy,
            item.SliceBase64,
            item.HeatmapBase64,
            item.CreatedAtUtc,
        });
    }

    [HttpDelete("history/{id:int}")]
    public async Task<IActionResult> DeleteResult(int id)
    {
        var userId = GetUserId();
        if (userId is null)
            return Unauthorized();

        var item = await _db.AnalysisResults
            .FirstOrDefaultAsync(r => r.Id == id && r.UserId == userId.Value);

        if (item == null)
            return NotFound(new { detail = "Result not found." });

        _db.AnalysisResults.Remove(item);
        await _db.SaveChangesAsync();

        return NoContent();
    }

    private int? GetUserId()
    {
        var raw = User.FindFirstValue(ClaimTypes.NameIdentifier);
        return int.TryParse(raw, out var id) ? id : null;
    }
}