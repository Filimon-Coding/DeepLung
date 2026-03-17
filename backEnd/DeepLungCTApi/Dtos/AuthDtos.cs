using System.Text.Json.Serialization;

namespace DeepLungCTApi.Dtos;

public class RegisterRequest
{
    public string Email { get; set; } = "";
    public string Password { get; set; } = "";

    // Accept frontend snake_case
    [JsonPropertyName("confirm_password")]
    public string ConfirmPassword { get; set; } = "";

    public string Role { get; set; } = "doctor";
}

public class LoginRequest
{
    /// <summary>Generated user ID (e.g. "yobe2801"). Used as the primary login identifier.</summary>
    public string UserId { get; set; } = "";
    public string Password { get; set; } = "";
}

public class AuthResponse
{
    public string UserId { get; set; } = "";
    public string Email { get; set; } = "";
    public string Role { get; set; } = "doctor";
    public string Token { get; set; } = "";
    public bool MustChangePassword { get; set; } = false;
}