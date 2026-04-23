using System.Text.Json.Serialization;

namespace DeepLungCTApi.Dtos;

public class PythonAnalyzeResponse
{
    [JsonPropertyName("filename")]
    public string Filename { get; set; } = "";

    [JsonPropertyName("content_type")]
    public string ContentType { get; set; } = "application/octet-stream";

    [JsonPropertyName("size_bytes")]
    public long SizeBytes { get; set; }

    [JsonPropertyName("prediction")]
    public string Prediction { get; set; } = "";

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("prob_benign")]
    public double ProbBenign { get; set; }

    [JsonPropertyName("prob_malignancy")]
    public double ProbMalignancy { get; set; }

    [JsonPropertyName("middle_slice_b64")]
    public string? MiddleSliceB64 { get; set; }

    [JsonPropertyName("gradcam_b64")]
    public string? GradcamB64 { get; set; }

    [JsonPropertyName("gradcam_nifti_b64")]
    public string? GradcamNiftiB64 { get; set; }

    [JsonPropertyName("slice_index")]
    public int SliceIndex { get; set; }

    [JsonPropertyName("slice_total")]
    public int SliceTotal { get; set; }

    [JsonPropertyName("cam_peak_x")]
    public int CamPeakX { get; set; }

    [JsonPropertyName("cam_peak_y")]
    public int CamPeakY { get; set; }

    [JsonPropertyName("cam_peak_z")]
    public int CamPeakZ { get; set; }
}

public class AnalyzeResponse
{
    public int AnalysisId { get; set; }

    public string Filename { get; set; } = "";
    public string ContentType { get; set; } = "application/octet-stream";
    public long SizeBytes { get; set; }

    public string Prediction { get; set; } = "";
    public double Confidence { get; set; }
    public double ProbBenign { get; set; }
    public double ProbMalignancy { get; set; }

    public string? MiddleSliceB64 { get; set; }
    public string? GradcamB64 { get; set; }
    // GradcamNiftiB64 is NOT returned here — it is fetched separately via
    // GET /api/history/{id}/gradcam-nifti to avoid a 60 MB JSON string in this response.

    public int SliceIndex { get; set; }
    public int SliceTotal { get; set; }
    public int CamPeakX { get; set; }
    public int CamPeakY { get; set; }
    public int CamPeakZ { get; set; }
}