import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { Button } from "../components/ui/button";
import { useAnalysis } from "../state/analysis-context";

export default function Analyze() {
  const navigate = useNavigate();
  const { file, setFile, runMockAnalysis } = useAnalysis();

  const [dragOver, setDragOver] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "running" | "done">("idle");

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const dropped = e.dataTransfer.files?.[0];
      if (dropped) setFile(dropped);
    },
    [setFile]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const run = async () => {
    if (!file) return;

    // Fake “upload + analyze” flow (ser realistisk ut på demo)
    setStatus("uploading");
    await new Promise((r) => setTimeout(r, 700));

    setStatus("running");
    await new Promise((r) => setTimeout(r, 900));

    runMockAnalysis();
    setStatus("done");

    navigate("/results");
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold text-[#1f3b63] text-center mb-4">ANALYZE</h1>

        <div className="text-center text-slate-600 text-sm mb-8">
          <p className="font-semibold">First upload a CT file in NIfTI format. Then Click Run analysis.</p>
          <p>A status indicator will display the progress of the upload and analysis stages.</p>
        </div>

        <div className="rounded-md p-6 mb-8 bg-[#d9e7f5]">
          <p className="font-bold text-sm mb-1">Upload file or select sample file</p>
          <p className="text-xs text-slate-600 mb-4">Drag and drop the file into the area below:</p>

          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-input")?.click()}
            className={[
              "border-2 border-dashed rounded-md cursor-pointer",
              "flex flex-col items-center justify-center py-16",
              dragOver ? "border-[#1f3b63] bg-white" : "border-slate-300 bg-white",
            ].join(" ")}
          >
            <div className="w-24 h-24 bg-slate-100 border border-slate-200 rounded flex items-center justify-center mb-3">
              <span className="text-slate-400 text-2xl">🖼️</span>
            </div>

            <p className="text-sm text-slate-600">
              {file ? (
                <>
                  <span className="font-semibold">Selected:</span> {file.name}
                </>
              ) : (
                "Click or drag a file here"
              )}
            </p>

            <input
              id="file-input"
              type="file"
              className="hidden"
              onChange={handleFileChange}
              accept=".nii,.nii.gz"
            />
          </div>

          <div className="mt-4 text-xs text-slate-700">
            <span className="font-bold">Status:</span>{" "}
            {status === "idle" && "Waiting for file"}
            {status === "uploading" && "Uploading..."}
            {status === "running" && "Running analysis..."}
            {status === "done" && "Done"}
          </div>
        </div>

        <div className="text-center">
          <Button
            className="px-12 py-3 text-sm"
            onClick={run}
            disabled={!file || status === "uploading" || status === "running"}
          >
            RUN ANALYSIS
          </Button>
        </div>
      </div>
    </Layout>
  );
}