using Microsoft.AspNetCore.Http;

namespace DeepLungCTApi.Dtos;

public class AnalyzeUploadRequest
{
    public IFormFile File { get; set; } = default!;
}