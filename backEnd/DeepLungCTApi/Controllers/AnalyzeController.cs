using System.Net.Http.Headers;
using System.Text.Json;
using DeepLungCTApi.Dtos;
using Microsoft.AspNetCore.Mvc;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
public class AnalyzeController : ControllerBase
{
    private readonly IHttpClientFactory _httpClientFactory;

    public AnalyzeController(IHttpClientFactory httpClientFactory)
    {
        _httpClientFactory = httpClientFactory;
    }

    [HttpPost("analyze")]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult<AnalyzeResponse>> Analyze([FromForm] AnalyzeUploadRequest request)
    {
        var file = request.File;
        if (file == null || file.Length == 0)
            return BadRequest("No file uploaded.");

        var client = _httpClientFactory.CreateClient("PythonService");

        // Build multipart form for PythonService
        using var form = new MultipartFormDataContent();

        using var fileStream = file.OpenReadStream();
        var fileContent = new StreamContent(fileStream);
        fileContent.Headers.ContentType = new MediaTypeHeaderValue(file.ContentType);

        // Python expects field name "file" (lowercase) in FastAPI example above
        form.Add(fileContent, "file", file.FileName);

        using var resp = await client.PostAsync("/analyze", form);
        var json = await resp.Content.ReadAsStringAsync();

        if (!resp.IsSuccessStatusCode)
            return StatusCode((int)resp.StatusCode, json);

        // Map Python JSON -> AnalyzeResponse
        // Your AnalyzeResponse uses: filename, content_type, size_bytes, prediction, confidence
        var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        var result = new AnalyzeResponse
        {
            filename = root.GetProperty("filename").GetString() ?? file.FileName,
            content_type = root.GetProperty("content_type").GetString() ?? file.ContentType,
            size_bytes = root.GetProperty("size_bytes").GetInt64(),
            prediction = root.GetProperty("prediction").GetString() ?? "Unknown",
            confidence = root.GetProperty("confidence").GetDouble(),
        };

        return Ok(result);
    }
}