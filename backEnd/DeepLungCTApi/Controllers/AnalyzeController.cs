using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text.Json;
using DeepLungCTApi.Data;
using DeepLungCTApi.Dtos;
using DeepLungCTApi.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
[Authorize]
public class AnalyzeController : ControllerBase
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly AppDbContext _db;

    public AnalyzeController(IHttpClientFactory httpClientFactory, AppDbContext db)
    {
        _httpClientFactory = httpClientFactory;
        _db = db;
    }

    [HttpPost("analyze")]
    [Consumes("multipart/form-data")]
    [RequestSizeLimit(200_000_000)]
    public async Task<ActionResult<AnalyzeResponse>> Analyze([FromForm] AnalyzeUploadRequest request)
    {
        var file = request.File;

        if (file == null || file.Length == 0)
            return BadRequest(new { detail = "No file uploaded." });

        var userIdRaw = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var email = User.FindFirstValue(ClaimTypes.Email);

        if (!int.TryParse(userIdRaw, out var userId) || string.IsNullOrWhiteSpace(email))
            return Unauthorized(new { detail = "Invalid user identity." });

        var userExists = await _db.Users.AnyAsync(u => u.Id == userId);
        if (!userExists)
            return Unauthorized(new { detail = "User not found." });

        var client = _httpClientFactory.CreateClient("PythonService");

        using var form = new MultipartFormDataContent();
        await using var stream = file.OpenReadStream();
        using var fileContent = new StreamContent(stream);

        fileContent.Headers.ContentType =
            new MediaTypeHeaderValue(file.ContentType ?? "application/octet-stream");

        form.Add(fileContent, "file", file.FileName);

        using var resp = await client.PostAsync("/analyze", form);
        var rawJson = await resp.Content.ReadAsStringAsync();

        if (!resp.IsSuccessStatusCode)
        {
            return StatusCode((int)resp.StatusCode, new
            {
                detail = "Python service failed.",
                pythonStatus = (int)resp.StatusCode,
                pythonResponse = rawJson
            });
        }

        var py = JsonSerializer.Deserialize<PythonAnalyzeResponse>(
            rawJson,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        if (py == null)
            return StatusCode(502, new { detail = "Invalid response from Python service." });

        var record = new AnalysisResult
        {
            UserId = userId,
            UserEmail = email,
            Filename = py.Filename,
            ContentType = py.ContentType,
            SizeBytes = py.SizeBytes,
            Prediction = py.Prediction,
            Confidence = py.Confidence,
            ProbBenign = py.ProbBenign,
            ProbMalignancy = py.ProbMalignancy,
            SliceBase64 = py.MiddleSliceB64,
            HeatmapBase64 = py.GradcamB64,
            CreatedAtUtc = DateTime.UtcNow,
        };

        _db.AnalysisResults.Add(record);
        await _db.SaveChangesAsync();

        return Ok(new AnalyzeResponse
        {
            AnalysisId = record.Id,
            Filename = record.Filename,
            ContentType = record.ContentType,
            SizeBytes = record.SizeBytes,
            Prediction = record.Prediction,
            Confidence = record.Confidence,
            ProbBenign = record.ProbBenign,
            ProbMalignancy = record.ProbMalignancy,
            MiddleSliceB64 = record.SliceBase64,
            GradcamB64 = record.HeatmapBase64,
        });
    }
}