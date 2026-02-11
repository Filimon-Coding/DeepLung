import React, { useState } from "react";
import "./DragAndDrop.css";

/**
 * DragAndDrop-komponenten håndterer opplastning av filer
 * ved hjelp av HTML5 Drag & Drop API.
 * Komponenten gir visuell feedback når en fil dras over området.
 */
export default function DragAndDrop() {

  /**
   * isActive brukes til å indikere om brukeren 
   * holder en fil over drop-sonen (vises visuelt som grønn kant)
   */
  const [isActive, setIsActive] = useState<boolean>(false);

  /**
   * Hjelpefunksjon som forhindrer nettleserens standard drag & drop-oppførsel
   * og stopper event-bubbling
   */
  const prevent = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
  };

  /**
   * Trigges når en fil kommer inn i drop-sonen. 
   * Aktiverer visuell feedback.
   */
  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(true);
  };

  /**
   * Trigges kontinuerlig mens filen holdes over drop-sonen.
   * Må ha preventDefault for at drop skal fungere.
   */
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(true);
  };

  /**
   * Trigges når filen forlater drop-sonen uten å bli sluppet.
   * Fjerner visuell feedback.
   */
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(false);
  };

  /**
   * Trigges når brukeren slipper filen i drop-sonen.
   * Her hentes filene fra DataTransfer-objektet.
   * 
   */
  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    prevent(e);
    setIsActive(false);

    // Henter filer fra drag-eventen
    const files: FileList | null = e.dataTransfer?.files ?? null;

    console.log("Dropped files:", files);

    //Eksempel: logger navnet på første fil 
    if (files && files.length > 0) {
      console.log("First file name:", files[0].name);
    }
  };

  return (
    /**
     * droparea er selve drop-sonen.
     * Klassen "green-border" legges til dynamisk
     * når isActive er true.
     */
    <div
      className={`droparea ${isActive ? "green-border" : ""}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Instruksjonstekst til brukeren */}
      <p className="drop-title">Drag & drop file here</p>
      <p className="drop-subtitle">No max file size</p>
    </div>
  );
}