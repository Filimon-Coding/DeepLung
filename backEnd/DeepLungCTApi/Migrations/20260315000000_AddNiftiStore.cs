using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace DeepLungCTApi.Migrations
{
    /// <inheritdoc />
    public partial class AddNiftiStore : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "GradcamNiftiB64",
                table: "AnalysisResults",
                type: "TEXT",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "NiftiStorePath",
                table: "AnalysisResults",
                type: "TEXT",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(name: "GradcamNiftiB64", table: "AnalysisResults");
            migrationBuilder.DropColumn(name: "NiftiStorePath",  table: "AnalysisResults");
        }
    }
}
