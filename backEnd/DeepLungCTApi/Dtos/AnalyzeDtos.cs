using System.Text.Json.Serialization;

namespace DeepLungCTApi.Dtos;

public class AnalyzeResponse
{
    public string filename { get; set; } = "";

    [JsonPropertyName("content_type")]
    public string content_type { get; set; } = "";

    [JsonPropertyName("size_bytes")]
    public long size_bytes { get; set; }

    public string prediction { get; set; } = "";
    public double confidence { get; set; }
}