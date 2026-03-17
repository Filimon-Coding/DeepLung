namespace DeepLungCTApi.Models;

public class User
{
    public int Id { get; set; }
    //// 

    /// <summary>Generated login ID, e.g. "yobe2801". Unique.</summary>
    public string? UserId { get; set; }

    public string Email { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public string Role { get; set; } = "doctor";

    // Profile fields (populated when admin approves an access request)
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Position { get; set; }
    public string? MobileNumber { get; set; }

    /// <summary>True when the user must change their password on next login.</summary>
    public bool MustChangePassword { get; set; } = false;

    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;

    public List<AnalysisResult> AnalysisResults { get; set; } = new();
}