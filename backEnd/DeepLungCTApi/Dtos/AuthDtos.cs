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
    public string Email { get; set; } = "";
    public string Password { get; set; } = "";
}

public class AuthResponse
{
    public string Email { get; set; } = "";
    public string Role { get; set; } = "doctor";
    public string Token { get; set; } = "";
}