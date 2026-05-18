using System.Text;
using System.Security.Claims;
using DeepLungCTApi.Data;
using DeepLungCTApi.Models;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SupportNonNullableReferenceTypes();

    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "Enter: Bearer {your JWT token}"
    });

    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("Default")));

builder.Services.AddCors(options =>
{
    options.AddPolicy("dev", policy =>
        policy
            .WithOrigins(
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            )
            .AllowAnyHeader()
            .AllowAnyMethod());
});

builder.Services.AddHttpClient("PythonService", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["PythonService:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(600);
});

var jwtSecret = builder.Configuration["Jwt:Secret"]!;
var signingKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret));

builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = signingKey,
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();

    // Seed default admin account if none exists
    if (!db.Users.Any(u => u.Role == "admin"))
    {
        db.Users.Add(new User
        {
            UserId = "admin01",
            Email = "admin@deeplungct.local",
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin@2026"),
            Role = "admin",
            FirstName = "Admin",
            LastName = "User",
            MustChangePassword = true,
            CreatedAtUtc = DateTime.UtcNow,
        });
        db.SaveChanges();
    }
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("dev");

app.UseHttpsRedirection();

app.UseAuthentication();

app.Use(async (context, next) =>
{
    var path = context.Request.Path;
    var canChangePassword =
        path.Equals("/api/change-password", StringComparison.OrdinalIgnoreCase);

    if (path.StartsWithSegments("/api") &&
        !canChangePassword &&
        context.User.Identity?.IsAuthenticated == true)
    {
        var userIdStr = context.User.FindFirstValue(ClaimTypes.NameIdentifier);

        if (int.TryParse(userIdStr, out var userId))
        {
            var db = context.RequestServices.GetRequiredService<AppDbContext>();
            var mustChangePassword = await db.Users
                .Where(u => u.Id == userId)
                .Select(u => u.MustChangePassword)
                .FirstOrDefaultAsync();

            if (mustChangePassword)
            {
                context.Response.StatusCode = StatusCodes.Status403Forbidden;
                await context.Response.WriteAsJsonAsync(new
                {
                    detail = "Password must be changed before continuing."
                });
                return;
            }
        }
    }

    await next();
});

app.UseAuthorization();

app.MapControllers();

app.Run();
