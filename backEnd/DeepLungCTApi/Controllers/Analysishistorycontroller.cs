using System.Security.Claims;
using DeepLungCTApi.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
[Authorize]
public class AnalysisHistoryController(AppDbContext db) : ControllerBase
{
    [HttpGet("history")]
    public async Task<IActionResult> GetHistory([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var userId = GetUserId();
        if (userId is null) return Unauthorized();

        page     = Math.Max(page, 1);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var query = db.AnalysisResults
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
                HasNifti = r.NiftiStorePath != null,
            })
            .ToListAsync();

        return Ok(new { total, page, pageSize, items });
    }

    [HttpGet("history/{id:int}")]
    public async Task<IActionResult> GetDetail(int id)
    {
        var userId = GetUserId();
        if (userId is null) return Unauthorized();

        var item = await db.AnalysisResults
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
            item.GradcamNiftiB64,
            item.SliceIndex,
            item.SliceTotal,
            item.CamPeakX,
            item.CamPeakY,
            item.CamPeakZ,
            item.CreatedAtUtc,
            HasNifti = item.NiftiStorePath != null,
        });
    }

    /// <summary>Stream the stored NIfTI file so the frontend can load it in the 3-D viewer.</summary>
    [HttpGet("history/{id:int}/nifti")]
    public async Task<IActionResult> GetNifti(int id)
    {
        var userId = GetUserId();
        if (userId is null) return Unauthorized();

        var item = await db.AnalysisResults
            .FirstOrDefaultAsync(r => r.Id == id && r.UserId == userId.Value);

        if (item == null)
            return NotFound(new { detail = "Result not found." });

        if (string.IsNullOrEmpty(item.NiftiStorePath) || !System.IO.File.Exists(item.NiftiStorePath))
            return NotFound(new { detail = "NIfTI file not available for this record." });

        var stream = System.IO.File.OpenRead(item.NiftiStorePath);
        return File(stream, "application/gzip", item.Filename);
    }

    [HttpDelete("history/{id:int}")]
    public async Task<IActionResult> DeleteResult(int id)
    {
        var userId = GetUserId();
        if (userId is null) return Unauthorized();

        var item = await db.AnalysisResults
            .FirstOrDefaultAsync(r => r.Id == id && r.UserId == userId.Value);

        if (item == null)
            return NotFound(new { detail = "Result not found." });

        // Delete stored NIfTI file from disk
        if (!string.IsNullOrEmpty(item.NiftiStorePath) && System.IO.File.Exists(item.NiftiStorePath))
            System.IO.File.Delete(item.NiftiStorePath);

        db.AnalysisResults.Remove(item);
        await db.SaveChangesAsync();

        return NoContent();
    }

    private int? GetUserId()
    {
        var raw = User.FindFirstValue(ClaimTypes.NameIdentifier);
        return int.TryParse(raw, out var id) ? id : null;
    }
}
