using DeepLungCTApi.Models;
using Microsoft.EntityFrameworkCore;

namespace DeepLungCTApi.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    public DbSet<User> Users => Set<User>();
    public DbSet<AnalysisResult> AnalysisResults => Set<AnalysisResult>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>()
            .HasIndex(u => u.Email)
            .IsUnique();

        modelBuilder.Entity<AnalysisResult>()
            .HasOne(r => r.User)
            .WithMany(u => u.AnalysisResults)
            .HasForeignKey(r => r.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<AnalysisResult>()
            .HasIndex(r => r.UserId);

        modelBuilder.Entity<AnalysisResult>()
            .Property(r => r.CreatedAtUtc)
            .HasDefaultValueSql("CURRENT_TIMESTAMP");

        base.OnModelCreating(modelBuilder);
    }
}