namespace DeepLungCTApi.Models;

public class AnalysisResult
{
    public int Id { get; set; }

    // Link result to the user who ran the analysis
    public int UserId { get; set; }
    public User? User { get; set; }

    public string UserEmail { get; set; } = "";

    public string Filename { get; set; } = "";
    public string ContentType { get; set; } = "application/octet-stream";
    public long SizeBytes { get; set; }

    public string Prediction { get; set; } = "";
    public double Confidence { get; set; }
    public double ProbBenign { get; set; }
    public double ProbMalignancy { get; set; }

    // Save images from Python response so history detail works
    public string? SliceBase64 { get; set; }
    public string? HeatmapBase64 { get; set; }

    // 3-D Grad-CAM NIfTI (small volume, stored as base64 text)
    public string? GradcamNiftiB64 { get; set; }

    // Slice / Grad-CAM spatial metadata from the Python inference
    public int SliceIndex { get; set; }
    public int SliceTotal { get; set; }
    public int CamPeakX  { get; set; }
    public int CamPeakY  { get; set; }
    public int CamPeakZ  { get; set; }

    // Path to the original uploaded NIfTI file saved on disk
    public string? NiftiStorePath { get; set; }

    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
}