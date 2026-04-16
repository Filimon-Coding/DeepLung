using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace DeepLungCTApi.Migrations
{
    /// <inheritdoc />
    public partial class AddSliceAndCamPeakFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "CamPeakX",
                table: "AnalysisResults",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "CamPeakY",
                table: "AnalysisResults",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "CamPeakZ",
                table: "AnalysisResults",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "SliceIndex",
                table: "AnalysisResults",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "SliceTotal",
                table: "AnalysisResults",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "CamPeakX",
                table: "AnalysisResults");

            migrationBuilder.DropColumn(
                name: "CamPeakY",
                table: "AnalysisResults");

            migrationBuilder.DropColumn(
                name: "CamPeakZ",
                table: "AnalysisResults");

            migrationBuilder.DropColumn(
                name: "SliceIndex",
                table: "AnalysisResults");

            migrationBuilder.DropColumn(
                name: "SliceTotal",
                table: "AnalysisResults");
        }
    }
}
