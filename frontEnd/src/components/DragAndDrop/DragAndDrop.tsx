import React, { useRef, useState } from "react";

type DragAndDropProps = {
  onFileSelected: (file: File) => void;
};

const ACCEPTED = ".nii,.nii.gz";
const ACCEPTED_MIME = ["application/gzip", "application/x-gzip", ""];

function isNifti(file: File): boolean {
  return file.name.endsWith(".nii") || file.name.endsWith(".nii.gz");
}

export default function DragAndDrop({ onFileSelected }: DragAndDropProps) {
  const [isActive, setIsActive] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const prevent = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleFile = (file: File) => {
    if (!isNifti(file)) {
      setErrorMsg("Only .nii or .nii.gz files are accepted.");
      return;
    }
    setErrorMsg(null);
    onFileSelected(file);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => { prevent(e); setIsActive(true); };
  const handleDragOver  = (e: React.DragEvent<HTMLDivElement>) => { prevent(e); setIsActive(true); };
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => { prevent(e); setIsActive(false); };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(false);
    const files = e.dataTransfer?.files;
    if (!files || files.length === 0) return;
    handleFile(files[0]);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    // Reset so the same file can be re-selected
    e.target.value = "";
  };

  return (
    <>
      <div
        className={`droparea ${isActive ? "green-border" : ""}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        style={{ cursor: "pointer" }}
      >
        {/* Hidden file input for click-to-browse */}
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          style={{ display: "none" }}
          onChange={handleInputChange}
        />

        <div>
          <p className="drop-title">Drag & drop or click to browse</p>
          <p className="drop-subtitle">Accepted formats: .nii, .nii.gz</p>
        </div>
      </div>

      {errorMsg && (
        <p className="error-text" style={{ marginTop: "0.75rem" }}>
          {errorMsg}
        </p>
      )}
    </>
  );
}