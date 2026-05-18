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
    private readonly IWebHostEnvironment _env;

    public AnalyzeController(IHttpClientFactory httpClientFactory, AppDbContext db, IWebHostEnvironment env)
    {
        _httpClientFactory = httpClientFactory;
        _db = db;
        _env = env;
    }

    [HttpPost("analyze")]
    [Consumes("multipart/form-data")]
    [RequestSizeLimit(500_000_000)]
    [RequestFormLimits(MultipartBodyLengthLimit = 500_000_000)]
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

        // Read the uploaded file bytes once so we can both save to disk and forward to Python
        using var memStream = new MemoryStream();
        await file.CopyToAsync(memStream);
        var fileBytes = memStream.ToArray();

        // Save NIfTI file to disk for later 3-D viewing from history
        var storeDir = Path.Combine(_env.ContentRootPath, "nifti_store");
        Directory.CreateDirectory(storeDir);
        var storeName = $"{Guid.NewGuid():N}{Path.GetExtension(file.FileName)}";
        var storePath = Path.Combine(storeDir, storeName);
        await System.IO.File.WriteAllBytesAsync(storePath, fileBytes);

        // Forward to Python service
        var client = _httpClientFactory.CreateClient("PythonService");

        using var form = new MultipartFormDataContent();
        using var fileContent = new ByteArrayContent(fileBytes);
        fileContent.Headers.ContentType =
            new MediaTypeHeaderValue(file.ContentType ?? "application/octet-stream");
        form.Add(fileContent, "file", file.FileName);

        using var resp = await client.PostAsync("/analyze", form);
        var rawJson = await resp.Content.ReadAsStringAsync();

        if (!resp.IsSuccessStatusCode)
        {
            // Clean up saved file if Python failed
            System.IO.File.Delete(storePath);
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
        {
            System.IO.File.Delete(storePath);
            return StatusCode(502, new { detail = "Invalid response from Python service." });
        }

        var record = new AnalysisResult
        {
            UserId         = userId,
            UserEmail      = email,
            Filename       = py.Filename,
            ContentType    = py.ContentType,
            SizeBytes      = py.SizeBytes,
            Prediction     = py.Prediction,
            Confidence     = py.Confidence,
            ProbBenign     = py.ProbBenign,
            ProbMalignancy = py.ProbMalignancy,
            SliceBase64    = py.MiddleSliceB64,
            HeatmapBase64  = py.GradcamB64,
            CamCachePath   = py.CamCachePath,  // NIfTI built on first GET /gradcam-nifti
            SliceIndex     = py.SliceIndex,
            SliceTotal     = py.SliceTotal,
            CamPeakX       = py.CamPeakX,
            CamPeakY       = py.CamPeakY,
            CamPeakZ       = py.CamPeakZ,
            NiftiStorePath = storePath,
            CreatedAtUtc   = DateTime.UtcNow,
        };

        _db.AnalysisResults.Add(record);
        await _db.SaveChangesAsync();

        return Ok(new AnalyzeResponse
        {
            AnalysisId     = record.Id,
            Filename       = record.Filename,
            ContentType    = record.ContentType,
            SizeBytes      = record.SizeBytes,
            Prediction     = record.Prediction,
            Confidence     = record.Confidence,
            ProbBenign     = record.ProbBenign,
            ProbMalignancy = record.ProbMalignancy,
            MiddleSliceB64 = record.SliceBase64,
            GradcamB64     = record.HeatmapBase64,
            // GradcamNiftiB64 intentionally omitted — fetch via GET /api/history/{id}/gradcam-nifti
            SliceIndex     = py.SliceIndex,
            SliceTotal     = py.SliceTotal,
            CamPeakX       = py.CamPeakX,
            CamPeakY       = py.CamPeakY,
            CamPeakZ       = py.CamPeakZ,
        });
    }
}
