import React, { useState } from "react";
import "./DragAndDrop.css";

type DragAndDropProps = {
  /**
   * Callback fired when the user drops a file into the drop zone.
   * The parent component (AnalyzePage) can store the file in state.
   */
  onFileSelected: (file: File) => void;
};

/**
 * DragAndDrop
 *
 * Handles file upload using the HTML5 Drag & Drop API.
 * Provides visual feedback when a file is dragged over the drop area.
 */
export default function DragAndDrop({ onFileSelected }: DragAndDropProps) {
  /**
   * Indicates whether the user is currently dragging a file over the drop zone
   * (used to toggle visual feedback like a green border).
   */
  const [isActive, setIsActive] = useState<boolean>(false);

  /**
   * Helper function that prevents the browser's default drag & drop behavior
   * and stops event bubbling.
   */
  const prevent = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
  };

  /**
   * Fired when a file enters the drop zone.
   * Enables visual feedback.
   */
  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(true);
  };

  /**
   * Fired continuously while the file is over the drop zone.
   * Must call preventDefault for the drop event to work.
   */
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(true);
  };

  /**
   * Fired when the file leaves the drop zone without being dropped.
   * Disables visual feedback.
   */
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(false);
  };

  /**
   * Fired when the user drops the file in the drop zone.
   * Extracts the first file and passes it to the parent via onFileSelected.
   */
  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(false);

    // Extract files from the drop event
    const files: FileList | null = e.dataTransfer?.files ?? null;

    // Only proceed if at least one file was dropped
    if (!files || files.length === 0) return;

    const file = files[0];

    // Pass the file to the parent (AnalyzePage)
    onFileSelected(file);
  };

  return (
    <div
      className={`droparea ${isActive ? "green-border" : ""}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <p className="drop-title">Drag & drop file here</p>
      <p className="drop-subtitle">No max file size</p>
    </div>
  );
}