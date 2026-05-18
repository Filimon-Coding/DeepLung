using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace DeepLungCTApi.Migrations
{
    /// <inheritdoc />
    public partial class AddCamCachePath : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "CamCachePath",
                table: "AnalysisResults",
                type: "TEXT",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "CamCachePath",
                table: "AnalysisResults");
        }
    }
}
