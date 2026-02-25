import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { Button } from "../components/ui/button";
import { useAnalysis } from "../state/analysis-context";

export default function Results() {
  const navigate = useNavigate();
  const { file, prediction, heatmapUrl, reset } = useAnalysis();

  const predictedClass = prediction?.predictedClass ?? "Unknown";
  const confidence = prediction?.confidence ?? 0;

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold text-[#1f3b63] text-center mb-4">ANALYSIS RESULTS</h1>

        <div className="text-center text-slate-600 text-sm mb-8">
          <p>This page presents the model output for the uploaded CT examination.</p>
          <p>The results include a predicted class and a confidence score,</p>
          <p>as well as a heatmap-based visualisation indicating which regions contributed most to the model's decision.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-8">
          <div className="text-center">
            <h3 className="font-bold text-sm mb-3">Uploaded file</h3>
            <div className="bg-slate-100 border border-slate-200 rounded w-[200px] h-[200px] mx-auto flex items-center justify-center">
              <span className="text-slate-500 text-xs">
                {file ? file.name : "No file"}
              </span>
            </div>
          </div>

          <div className="text-center">
            <h3 className="font-bold text-sm mb-3">Model attention (Heatmap)</h3>
            <div className="bg-slate-100 border border-slate-200 rounded w-[200px] h-[200px] mx-auto flex items-center justify-center overflow-hidden">
              {/* Placeholder: legg en fil i public/heatmap-placeholder.png */}
              {heatmapUrl ? (
                <img
                  src={heatmapUrl}
                  alt="Heatmap"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).style.display = "none";
                  }}
                />
              ) : (
                <span className="text-slate-500 text-xs">Heatmap</span>
              )}
            </div>
          </div>
        </div>

        <div className="rounded-md p-6 text-center mb-8 bg-slate-100 border border-slate-200">
          <p className="text-base mb-2">
            <span className="font-bold">Predicted class:</span>{" "}
            <span className="italic">{predictedClass}</span>
          </p>
          <p className="text-base">
            <span className="font-bold">Confidence score:</span>{" "}
            <span className="italic">[{confidence}%]</span>
          </p>
        </div>

        <div className="text-center mb-8">
          <Button
            variant="outline"
            className="px-8 py-3 text-xs"
            onClick={() => {
              reset();
              navigate("/analyze");
            }}
          >
            RUN ANALYSIS AGAIN OR ANALYZE ANOTHER FILE
          </Button>
        </div>

        <p className="text-center text-slate-600 text-xs italic">
          <span className="font-bold not-italic">Note:</span> The confidence score reflects the model's estimated likelihood
          for the predicted class and should be interpreted as a probabilistic output rather than a definitive conclusion.
        </p>
      </div>
    </Layout>
  );
}