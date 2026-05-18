import { Outlet } from "react-router-dom";
import { Suspense } from "react";
import Navbar from "./components/Navbar";
import Spinner from "./components/Spinner";

function App() {
  return (
    <>
      <Navbar />
      <Suspense fallback={<Spinner />}>
        <Outlet />
      </Suspense>
    </>
  );
}

export default App;