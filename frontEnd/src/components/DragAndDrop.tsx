import { useRef, useState } from "react";

type DragAndDropProps = {
  onFileSelected: (file: File) => void;
};

function isValidNiftiFile(file: File): boolean {
  const lower = file.name.toLowerCase();
  return lower.endsWith(".nii") || lower.endsWith(".nii.gz");
}

function DragAndDrop({ onFileSelected }: DragAndDropProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  function handleFile(file: File | null) {
    if (!file) return;

    if (!isValidNiftiFile(file)) {
      setLocalError("Only .nii and .nii.gz files are supported.");
      return;
    }

    setLocalError(null);
    onFileSelected(file);
  }

  function openFileDialog() {
    inputRef.current?.click();
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selectedFile = e.target.files?.[0] ?? null;
    handleFile(selectedFile);

    // reset value so same file can be picked again later
    e.currentTarget.value = "";
  }

  function onDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(true);
  }

  function onDragLeave(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(false);
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files?.[0] ?? null;
    handleFile(droppedFile);
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLDivElement>) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      openFileDialog();
    }
  }

  return (
    <div>
      <div
        className={`dropzone ${dragActive ? "drag-active" : ""}`}
        onClick={openFileDialog}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onKeyDown={onKeyDown}
        role="button"
        tabIndex={0}
        aria-label="Upload NIfTI file"
      >
        <p className="drop-title">Click to upload or drag and drop</p>
        <p className="drop-subtitle">Supported formats: .nii, .nii.gz</p>

        <input
          ref={inputRef}
          type="file"
          accept=".nii,.nii.gz,application/gzip"
          onChange={onInputChange}
          style={{ display: "none" }}
        />
      </div>

      {localError && <p className="error-text">{localError}</p>}
    </div>
  );
}

export default DragAndDrop;