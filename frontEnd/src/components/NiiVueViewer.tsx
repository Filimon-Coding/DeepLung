import { useEffect, useRef, useState, useCallback } from "react";
import { Niivue, NVImage } from "@niivue/niivue";

type Props = {
  niftiFile: File;
  gradcamNiftiB64: string | null;
};

// CT Hounsfield window presets
const CT_PRESETS = [
  { label: "Lung",        cal_min: -1400, cal_max: 200  },
  { label: "Soft Tissue", cal_min: -175,  cal_max: 275  },
  { label: "Bone",        cal_min: -200,  cal_max: 1000 },
  { label: "Brain",       cal_min: 0,     cal_max: 80   },
];

// NiiVue SLICE_TYPE enum values (confirmed from source)
const SLICE = { AXIAL: 0, CORONAL: 1, SAGITTAL: 2, MULTIPLANAR: 3, RENDER: 4 };

type ViewMode = "4panel" | "axial" | "coronal" | "sagittal" | "3d";

const VIEW_SLICE: Record<ViewMode, number> = {
  "4panel":  SLICE.MULTIPLANAR,
  axial:     SLICE.AXIAL,
  coronal:   SLICE.CORONAL,
  sagittal:  SLICE.SAGITTAL,
  "3d":      SLICE.RENDER,
};

type LocationData = {
  vox:    number[];           // [x, y, z] voxel coords
  mm:     number[];           // [x, y, z] world mm coords
  values: { value: number }[];
};

type VolDims = { x: number; y: number; z: number };

export default function NiiVueViewer({ niftiFile, gradcamNiftiB64 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nvRef     = useRef<Niivue | null>(null);

  const [view,       setView]       = useState<ViewMode>("4panel");
  const [preset,     setPreset]     = useState(0);
  const [showCam,    setShowCam]    = useState(true);
  const [camOpacity, setCamOpacity] = useState(0.72);
  const [loc,        setLoc]        = useState<LocationData | null>(null);
  const [dims,       setDims]       = useState<VolDims | null>(null);
  const [ready,      setReady]      = useState(false);
  const [error,      setError]      = useState<string | null>(null);
  const [fullscreen, setFullscreen] = useState(false);

  // ── Initialise NiiVue ──────────────────────────────────────────
  useEffect(() => {
    if (!canvasRef.current) return;
    let cancelled = false;

    const nv = new Niivue({
      backColor:                [0.06, 0.07, 0.09, 1],
      crosshairColor:           [0.18, 0.82, 1, 0.9],
      crosshairWidth:           1,
      show3Dcrosshair:          true,
      isOrientationTextVisible: true,
      isColorbar:               false,
      multiplanarShowRender:    1,   // ALWAYS – 4th panel = 3-D render
      multiplanarLayout:        2,   // GRID   – 2 × 2
      multiplanarEqualSize:     true,
      multiplanarPadPixels:     3,
      sliceType:                SLICE.MULTIPLANAR,
      loadingText:              "Loading volume…",
    });

    nvRef.current = nv;

    nv.onLocationChange = (data: unknown) => {
      if (cancelled) return;
      const d = data as LocationData;
      setLoc({ vox: d.vox, mm: d.mm, values: d.values });
    };

    async function init() {
      try {
        const canvas = canvasRef.current!;

        // Wait for the browser to complete grid/flex layout so canvas.offsetWidth
        // is the real rendered size before NiiVue reads it in attachToCanvas.
        await new Promise<void>(resolve =>
          requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
        );
        if (cancelled) return;

        // Stamp the canvas pixel buffer to match the CSS-rendered size
        if (canvas.offsetWidth > 0)  canvas.width  = canvas.offsetWidth;
        if (canvas.offsetHeight > 0) canvas.height = canvas.offsetHeight;

        await nv.attachToCanvas(canvas);
        if (cancelled) return;

        const ctImage = await NVImage.loadFromFile({
          file:     niftiFile,
          colormap: "gray",
          opacity:  1,
          cal_min:  CT_PRESETS[0].cal_min,
          cal_max:  CT_PRESETS[0].cal_max,
        });
        nv.addVolume(ctImage);

        // Read volume dimensions from header
        const hdr = (nv.volumes[0] as any).hdr;
        if (hdr?.dims) {
          setDims({ x: hdr.dims[1], y: hdr.dims[2], z: hdr.dims[3] });
        }

        if (gradcamNiftiB64) {
          const camImage = await NVImage.loadFromBase64({
            base64:   gradcamNiftiB64,
            name:     "gradcam.nii.gz",
            colormap: "warm",   // dark-red → orange → bright yellow, more vivid than "hot"
            opacity:  0.72,
            cal_min:  0.01,     // 0.0 voxels (background) are transparent; active region starts at 0.3+
            cal_max:  1.0,
          });
          nv.addVolume(camImage);
        }

        if (!cancelled) {
          setReady(true);
          // Belt-and-suspenders: redraw after React paints the inspector bar
          [50, 200, 600].forEach(ms =>
            setTimeout(() => { if (!cancelled) nv.resizeListener(); }, ms)
          );
        }
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load volume");
      }
    }

    init();
    return () => {
      cancelled = true;
      nvRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [niftiFile, gradcamNiftiB64]);

  // ── Sync view mode ─────────────────────────────────────────────
  useEffect(() => {
    if (!nvRef.current || !ready) return;
    nvRef.current.setSliceType(VIEW_SLICE[view]);
    if (view === "4panel") (nvRef.current as any).opts.multiplanarShowRender = 1;
  }, [view, ready]);

  // ── Sync CAM overlay ───────────────────────────────────────────
  useEffect(() => {
    if (!nvRef.current || !ready || !gradcamNiftiB64) return;
    const vols = nvRef.current.volumes;
    if (vols.length < 2) return;
    vols[1].opacity = showCam ? camOpacity : 0;
    nvRef.current.updateGLVolume();
  }, [showCam, camOpacity, ready, gradcamNiftiB64]);

  // ── Apply CT window preset ─────────────────────────────────────
  const applyPreset = useCallback((idx: number) => {
    setPreset(idx);
    if (!nvRef.current || !ready) return;
    const vol = nvRef.current.volumes[0];
    if (!vol) return;
    vol.cal_min = CT_PRESETS[idx].cal_min;
    vol.cal_max = CT_PRESETS[idx].cal_max;
    nvRef.current.updateGLVolume();
  }, [ready]);

  // ── Fullscreen toggle ──────────────────────────────────────────
  const toggleFullscreen = useCallback(() => {
    setFullscreen((f) => {
      const next = !f;
      document.body.classList.toggle("nv-is-fullscreen", next);
      return next;
    });
    setTimeout(() => nvRef.current?.resizeListener(), 50);
  }, []);

  // Clean up body class if component unmounts while fullscreen
  useEffect(() => {
    return () => { document.body.classList.remove("nv-is-fullscreen"); };
  }, []);

  const viewButtons: { label: string; value: ViewMode }[] = [
    { label: "4-Panel",  value: "4panel"   },
    { label: "Axial",    value: "axial"    },
    { label: "Coronal",  value: "coronal"  },
    { label: "Sagittal", value: "sagittal" },
    { label: "3-D",      value: "3d"       },
  ];

  // Cursor data for the inspector panel
  const vox = loc?.vox ?? null;
  const hu  = loc?.values?.[0]?.value ?? null;

  return (
    <div className={`nv-viewer${fullscreen ? " nv-fullscreen" : ""}`}>

      {/* ── Toolbar ───────────────────────────────────────────── */}
      <div className="nv-toolbar">
        <div className="nv-toolbar-group">
          {viewButtons.map((b) => (
            <button
              key={b.value}
              className={`nv-btn${view === b.value ? " nv-btn-active" : ""}`}
              onClick={() => setView(b.value)}
            >
              {b.label}
            </button>
          ))}
        </div>

        <div className="nv-toolbar-group">
          <span className="nv-label">Window</span>
          {CT_PRESETS.map((p, i) => (
            <button
              key={p.label}
              className={`nv-btn${preset === i ? " nv-btn-active" : ""}`}
              onClick={() => applyPreset(i)}
            >
              {p.label}
            </button>
          ))}
        </div>

        <div className="nv-toolbar-group nv-toolbar-right">
          {gradcamNiftiB64 && (
            <>
              <label className="nv-toggle">
                <input type="checkbox" checked={showCam}
                  onChange={(e) => setShowCam(e.target.checked)} />
                Grad-CAM
              </label>
              {showCam && (
                <label className="nv-opacity-label">
                  <input type="range" min={0} max={1} step={0.05}
                    value={camOpacity}
                    onChange={(e) => setCamOpacity(parseFloat(e.target.value))} />
                  <span>{Math.round(camOpacity * 100)}%</span>
                </label>
              )}
            </>
          )}
          <button className="nv-btn nv-btn-icon" title={fullscreen ? "Exit fullscreen" : "Fullscreen"}
            onClick={toggleFullscreen}>
            {fullscreen ? "✕" : "⛶"}
          </button>
        </div>
      </div>

      {/* ── Canvas ────────────────────────────────────────────── */}
      <div className="nv-canvas-wrap">
        <canvas ref={canvasRef} className="nv-canvas" />
        {!ready && !error && <div className="nv-overlay-msg">Loading 3-D volume…</div>}
        {error       && <div className="nv-overlay-msg nv-overlay-error">{error}</div>}
      </div>

      {/* ── Cursor Inspector (ITK-SNAP style) ─────────────────── */}
      {ready && (
        <div className="nv-inspector">
          <div className="nv-inspector-section">
            <span className="nv-inspector-title">Cursor Position</span>
            <div className="nv-inspector-coords">
              <span><em>x</em>{vox ? vox[0] : "—"}</span>
              <span><em>y</em>{vox ? vox[1] : "—"}</span>
              <span><em>z</em>{vox ? vox[2] : "—"}</span>
            </div>
          </div>

          {dims && vox && (
            <div className="nv-inspector-section">
              <span className="nv-inspector-title">Slice</span>
              <div className="nv-inspector-slices">
                <span>Axial<em>{vox[2]} / {dims.z}</em></span>
                <span>Coronal<em>{vox[1]} / {dims.y}</em></span>
                <span>Sagittal<em>{vox[0]} / {dims.x}</em></span>
              </div>
            </div>
          )}

          <div className="nv-inspector-section">
            <span className="nv-inspector-title">Intensity</span>
            <span className="nv-inspector-value">
              {hu !== null ? `${hu.toFixed(0)} HU` : "—"}
            </span>
          </div>

          <div className="nv-inspector-section nv-inspector-file">
            {niftiFile.name}
          </div>
        </div>
      )}
    </div>
  );
}
