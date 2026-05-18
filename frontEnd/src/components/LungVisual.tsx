import lungsImg from "../assets/lungs-3d.png?format=webp&quality=80&as=url";

function LungVisual() {
  return (
    <img
      src={lungsImg}
      alt="3D lung illustration"
      className="lung-img"
      loading="lazy"
      decoding="async"
      width="420"
      height="420"
    />
  );
}

export default LungVisual;
