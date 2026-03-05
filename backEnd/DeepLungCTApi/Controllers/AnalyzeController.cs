using DeepLungCTApi.Dtos;
using Microsoft.AspNetCore.Mvc;

namespace DeepLungCTApi.Controllers;

[ApiController]
[Route("api")]
public class AnalyzeController : ControllerBase
{
    [HttpPost("analyze")]
    [RequestSizeLimit(30_000_000)]
    public async Task<ActionResult<AnalyzeResponse>> Analyze([FromForm] IFormFile file)
    {
        if (file == null || file.Length == 0)
            return BadRequest("No file uploaded.");

        using var ms = new MemoryStream();
        await file.CopyToAsync(ms);

        // TODO: Koble på ekte ML senere
        var res = new AnalyzeResponse
        {
            filename = file.FileName,
            content_type = file.ContentType,
            size_bytes = file.Length,
            prediction = "Normal",
            confidence = 0.83
        };

        return Ok(res);
    }
}