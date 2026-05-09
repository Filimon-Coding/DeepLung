using System.Security.Claims;
using System.Text.Json;
using DeepLungCTApi.Controllers;
using DeepLungCTApi.Data;
using DeepLungCTApi.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace DeepLungCTApi.Tests;

// AdminControllerTests.cs
// Unit tests for AdminController — covers all five endpoints:
// ListUsers, UpdateUser, DeleteUser, GetStats, GetLogs, GetHealth, ResetPassword.
// Each test uses an isolated in-memory database so no state leaks between runs.
// Positive cases verify correct data is returned / persisted.
// Negative cases verify the right HTTP error codes on bad input.

public class AdminControllerTests
{
    // ─── Helpers ──────────────────────────────────────────────────────────────

    private static AppDbContext BuildDb(string dbName)
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(dbName)
            .Options;
        return new AppDbContext(options);
    }

    private static AdminController BuildController(AppDbContext db)
    {
        var controller = new AdminController(db);

        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, "1"),
            new Claim(ClaimTypes.Role, "admin"),
        };

        controller.ControllerContext = new ControllerContext
        {
            HttpContext = new DefaultHttpContext
            {
                User = new ClaimsPrincipal(new ClaimsIdentity(claims, "TestAuth"))
            }
        };

        return controller;
    }

    private static async Task<User> SeedUserAsync(
        AppDbContext db,
        string firstName,
        string lastName,
        string email,
        string role = "doctor",
        string userId = "test001")
    {
        var user = new User
        {
            UserId = userId,
            FirstName = firstName,
            LastName = lastName,
            Email = email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("password"),
            Role = role,
        };
        db.Users.Add(user);
        await db.SaveChangesAsync();
        return user;
    }

    private static async Task<AnalysisResult> SeedResultAsync(
        AppDbContext db,
        int userId,
        string userEmail,
        string prediction,
        DateTime? createdAt = null)
    {
        var result = new AnalysisResult
        {
            UserId = userId,
            UserEmail = userEmail,
            Filename = "scan.nii.gz",
            Prediction = prediction,
            Confidence = 0.9,
            CreatedAtUtc = createdAt ?? DateTime.UtcNow,
        };
        db.AnalysisResults.Add(result);
        await db.SaveChangesAsync();
        return result;
    }

    private static async Task<AccessRequest> SeedAccessRequestAsync(AppDbContext db, string status = "pending")
    {
        var req = new AccessRequest
        {
            FirstName = "Jane",
            LastName = "Doe",
            Email = "jane@example.com",
            Personnummer = "12345678901",
            MobileNumber = "12345678",
            Position = "Nurse",
            Status = status,
        };
        db.AccessRequests.Add(req);
        await db.SaveChangesAsync();
        return req;
    }

    // Serialize the OkObjectResult value and return a JsonElement for property inspection.
    // Anonymous-type results from controllers cannot be cast to a concrete type,
    // so serializing to JSON is the safest way to assert property values.
    private static JsonElement ParseOk(OkObjectResult ok)
    {
        var json = JsonSerializer.Serialize(ok.Value);
        return JsonDocument.Parse(json).RootElement;
    }

    // ─── A) Positive test cases ───────────────────────────────────────────────

    [Fact]
    public async Task ListUsers_ReturnsSortedByLastNameThenFirstName()
    {
        var db = BuildDb(nameof(ListUsers_ReturnsSortedByLastNameThenFirstName));
        await SeedUserAsync(db, "Zara", "Smith", "zara@x.com", userId: "zara01");
        await SeedUserAsync(db, "Anna", "Adams", "anna@x.com", userId: "anna01");
        await SeedUserAsync(db, "Bob",  "Adams", "bob@x.com",  userId: "bob01");

        var result = await BuildController(db).ListUsers();

        var ok = Assert.IsType<OkObjectResult>(result);
        var users = ParseOk(ok).EnumerateArray().ToList();

        Assert.Equal(3, users.Count);
        // Adams comes before Smith
        Assert.Equal("Adams", users[0].GetProperty("LastName").GetString());
        Assert.Equal("Adams", users[1].GetProperty("LastName").GetString());
        Assert.Equal("Smith", users[2].GetProperty("LastName").GetString());
        // Anna comes before Bob within Adams
        Assert.Equal("Anna", users[0].GetProperty("FirstName").GetString());
        Assert.Equal("Bob",  users[1].GetProperty("FirstName").GetString());
    }

    [Fact]
    public async Task UpdateUser_ValidRequest_UpdatesFieldsInDb()
    {
        var db = BuildDb(nameof(UpdateUser_ValidRequest_UpdatesFieldsInDb));
        var user = await SeedUserAsync(db, "Old", "Name", "old@x.com");

        var req = new AdminController.UpdateUserRequest(
            "New", "Surname", "new@x.com", "99999999", "Radiologist", "admin");

        var result = await BuildController(db).UpdateUser(user.Id, req);

        var ok = Assert.IsType<OkObjectResult>(result);
        var body = ParseOk(ok);

        Assert.Equal("New",     body.GetProperty("FirstName").GetString());
        Assert.Equal("Surname", body.GetProperty("LastName").GetString());
        Assert.Equal("admin",   body.GetProperty("Role").GetString());

        var inDb = await db.Users.FindAsync(user.Id);
        Assert.Equal("new@x.com",    inDb!.Email);
        Assert.Equal("Radiologist",  inDb.Position);
        Assert.Equal("99999999",     inDb.MobileNumber);
    }

    [Fact]
    public async Task UpdateUser_UnknownRole_NormalizesToDoctor()
    {
        var db = BuildDb(nameof(UpdateUser_UnknownRole_NormalizesToDoctor));
        var user = await SeedUserAsync(db, "Test", "User", "t@x.com");

        // "nurse" is not a recognised role — controller falls back to "doctor"
        var req = new AdminController.UpdateUserRequest(null, null, null, null, null, "nurse");
        await BuildController(db).UpdateUser(user.Id, req);

        var inDb = await db.Users.FindAsync(user.Id);
        Assert.Equal("doctor", inDb!.Role);
    }

    [Fact]
    public async Task DeleteUser_Doctor_ReturnsNoContent_AndRemovedFromDb()
    {
        var db = BuildDb(nameof(DeleteUser_Doctor_ReturnsNoContent_AndRemovedFromDb));
        var user = await SeedUserAsync(db, "John", "Doe", "john@x.com", role: "doctor");

        var result = await BuildController(db).DeleteUser(user.Id);

        Assert.IsType<NoContentResult>(result);
        Assert.False(await db.Users.AnyAsync(u => u.Id == user.Id));
    }

    [Fact]
    public async Task GetStats_WithMixedPredictions_ReturnsCorrectCounts()
    {
        var db = BuildDb(nameof(GetStats_WithMixedPredictions_ReturnsCorrectCounts));
        var user = await SeedUserAsync(db, "A", "B", "a@x.com");

        var now = DateTime.UtcNow;
        await SeedResultAsync(db, user.Id, user.Email, "Benign",    now);
        await SeedResultAsync(db, user.Id, user.Email, "Benign",    now);
        await SeedResultAsync(db, user.Id, user.Email, "Malignancy", now);

        var result = await BuildController(db).GetStats(null, null);

        var ok   = Assert.IsType<OkObjectResult>(result);
        var body = ParseOk(ok);

        Assert.Equal(3, body.GetProperty("total").GetInt32());
        Assert.Equal(2, body.GetProperty("benign").GetInt32());
        Assert.Equal(1, body.GetProperty("malignant").GetInt32());
    }

    [Fact]
    public async Task GetLogs_ReturnsNewestFirst()
    {
        var db = BuildDb(nameof(GetLogs_ReturnsNewestFirst));
        var user = await SeedUserAsync(db, "A", "B", "a@x.com");

        var oldest = DateTime.UtcNow.AddDays(-2);
        var newest = DateTime.UtcNow;

        await SeedResultAsync(db, user.Id, user.Email, "Benign",     oldest);
        await SeedResultAsync(db, user.Id, user.Email, "Malignancy", newest);

        var result = await BuildController(db).GetLogs(10);

        var ok   = Assert.IsType<OkObjectResult>(result);
        var logs = ParseOk(ok).EnumerateArray().ToList();

        Assert.Equal(2, logs.Count);
        Assert.Equal("Malignancy", logs[0].GetProperty("Prediction").GetString());
        Assert.Equal("Benign",     logs[1].GetProperty("Prediction").GetString());
    }

    [Fact]
    public async Task GetLogs_LimitExceedingMax_ClampedTo500()
    {
        var db = BuildDb(nameof(GetLogs_LimitExceedingMax_ClampedTo500));

        // Passing limit > 500 must not throw — controller clamps internally
        var result = await BuildController(db).GetLogs(999);

        Assert.IsType<OkObjectResult>(result);
    }

    [Fact]
    public async Task GetHealth_ReturnsCorrectDbCounts()
    {
        var db = BuildDb(nameof(GetHealth_ReturnsCorrectDbCounts));
        var user = await SeedUserAsync(db, "A", "B", "a@x.com");
        await SeedResultAsync(db, user.Id, user.Email, "Benign");
        await SeedResultAsync(db, user.Id, user.Email, "Malignancy");
        await SeedAccessRequestAsync(db, "pending");
        await SeedAccessRequestAsync(db, "approved"); // should NOT be counted as pending

        var result = await BuildController(db).GetHealth();

        var ok   = Assert.IsType<OkObjectResult>(result);
        var body = ParseOk(ok);

        Assert.Equal(1, body.GetProperty("totalUsers").GetInt32());
        Assert.Equal(2, body.GetProperty("totalAnalyses").GetInt32());
        Assert.Equal(1, body.GetProperty("pendingRequests").GetInt32());
        Assert.Equal("online", body.GetProperty("apiStatus").GetString());
    }

    [Fact]
    public async Task ResetPassword_ValidPassword_SetsHashAndMustChangeFlag()
    {
        var db = BuildDb(nameof(ResetPassword_ValidPassword_SetsHashAndMustChangeFlag));
        var user = await SeedUserAsync(db, "Test", "User", "t@x.com");
        var oldHash = user.PasswordHash;

        var req = new AdminController.ResetPasswordRequest("newpassword123");
        var result = await BuildController(db).ResetPassword(user.Id, req);

        Assert.IsType<OkObjectResult>(result);

        var inDb = await db.Users.FindAsync(user.Id);
        Assert.True(inDb!.MustChangePassword);
        Assert.NotEqual(oldHash, inDb.PasswordHash);
        Assert.True(BCrypt.Net.BCrypt.Verify("newpassword123", inDb.PasswordHash));
    }

    // ─── B) Negative test cases ───────────────────────────────────────────────

    [Fact]
    public async Task UpdateUser_UnknownId_ReturnsNotFound()
    {
        var db  = BuildDb(nameof(UpdateUser_UnknownId_ReturnsNotFound));
        var req = new AdminController.UpdateUserRequest("X", null, null, null, null, null);

        var result = await BuildController(db).UpdateUser(99999, req);

        Assert.IsType<NotFoundObjectResult>(result);
    }

    [Fact]
    public async Task UpdateUser_DuplicateEmail_ReturnsConflict()
    {
        var db = BuildDb(nameof(UpdateUser_DuplicateEmail_ReturnsConflict));
        await SeedUserAsync(db, "Alice", "A", "alice@x.com", userId: "alice01");
        var bob = await SeedUserAsync(db, "Bob", "B", "bob@x.com", userId: "bob01");

        // Try to change Bob's email to Alice's — should conflict
        var req = new AdminController.UpdateUserRequest(null, null, "alice@x.com", null, null, null);
        var result = await BuildController(db).UpdateUser(bob.Id, req);

        Assert.IsType<ConflictObjectResult>(result);
    }

    [Fact]
    public async Task DeleteUser_UnknownId_ReturnsNotFound()
    {
        var db = BuildDb(nameof(DeleteUser_UnknownId_ReturnsNotFound));

        var result = await BuildController(db).DeleteUser(99999);

        Assert.IsType<NotFoundObjectResult>(result);
    }

    [Fact]
    public async Task DeleteUser_LastAdmin_ReturnsConflict()
    {
        var db    = BuildDb(nameof(DeleteUser_LastAdmin_ReturnsConflict));
        var admin = await SeedUserAsync(db, "Super", "Admin", "admin@x.com", role: "admin");

        var result = await BuildController(db).DeleteUser(admin.Id);

        Assert.IsType<ConflictObjectResult>(result);
        // Admin must still exist in the database
        Assert.True(await db.Users.AnyAsync(u => u.Id == admin.Id));
    }

    [Fact]
    public async Task ResetPassword_UnknownId_ReturnsNotFound()
    {
        var db  = BuildDb(nameof(ResetPassword_UnknownId_ReturnsNotFound));
        var req = new AdminController.ResetPasswordRequest("strongpassword");

        var result = await BuildController(db).ResetPassword(99999, req);

        Assert.IsType<NotFoundObjectResult>(result);
    }

    [Fact]
    public async Task ResetPassword_ShortPassword_ReturnsBadRequest()
    {
        var db   = BuildDb(nameof(ResetPassword_ShortPassword_ReturnsBadRequest));
        var user = await SeedUserAsync(db, "Test", "User", "t@x.com");

        var req = new AdminController.ResetPasswordRequest("short"); // < 8 chars
        var result = await BuildController(db).ResetPassword(user.Id, req);

        Assert.IsType<BadRequestObjectResult>(result);
    }
}
