namespace DeepLungCTApi.Models;

public class User
{
    public int Id { get; set; }

    public string Email { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public string Role { get; set; } = "doctor";

    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;

    public List<AnalysisResult> AnalysisResults { get; set; } = new();
}