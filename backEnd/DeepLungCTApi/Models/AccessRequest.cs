namespace DeepLungCTApi.Models;

public class AccessRequest
{
    public int Id { get; set; }

    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;

    /// <summary>Norwegian personnummer (11 digits). Stored for admin use only.</summary>
    public string Personnummer { get; set; } = string.Empty;

    public string MobileNumber { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Position { get; set; } = string.Empty;

    /// <summary>"pending" | "approved" | "rejected"</summary>
    public string Status { get; set; } = "pending";

    public DateTime SubmittedAtUtc { get; set; } = DateTime.UtcNow;
}
