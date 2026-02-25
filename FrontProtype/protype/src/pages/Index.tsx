import Layout from "../components/Layout";
import { Button } from "../components/ui/button";

export default function Index() {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-6 py-12 text-center">
        <h1 className="text-4xl font-bold mb-6">AI-Assisted Lung CT Classification (Prototype)</h1>

        <p className="text-slate-600 font-semibold mb-8">
          This website demonstrates a simplified workflow for machine learning–based analysis of CT data:
        </p>

        <div className="space-y-2 text-sm mb-10">
          <p>
            <span className="font-bold">Upload:</span> You upload a CT file in NIfTI format.
          </p>
          <p>
            <span className="font-bold">Analysis:</span> The system runs a model that estimates the probability of relevant findings.
          </p>
          <p>
            <span className="font-bold">Visualisation:</span> A heatmap is displayed over CT slices to illustrate which regions the model attends to most strongly.
          </p>
          <p>
            <span className="font-bold">Output:</span> The system provides a prediction (e.g., “Cancer” / “No cancer”) along with a probability score.
          </p>
        </div>

        <p className="text-slate-600 font-semibold mb-4">
          Here, we provide a demonstration video illustrating how our website operates.
        </p>

        <div className="flex items-center justify-center gap-4 mb-6">
          <button className="text-sm font-semibold hover:opacity-70">▶ Play Video</button>
          <Button variant="outline" className="px-8 py-2 text-xs">
            CLICK HERE
          </Button>
        </div>

        <div className="bg-slate-100 border border-slate-200 rounded-md aspect-video flex items-center justify-center">
          <div className="text-slate-500 text-sm">Video Placeholder</div>
        </div>
      </div>
    </Layout>
  );
}