/*
	author: Veronika Šimková (xsimko14)
	file: App.tsx
*/

import { Navigate, Route, Routes } from "react-router";
import { AccidentRoutes } from "./routes/accident-routes";
import { TrafficJamRoutes } from "./routes/traffic-jam-routes";

function App() {
  return (
    <Routes>
      <Route path="/accidents/*" Component={AccidentRoutes} />
      <Route path="/traffic-jams/*" Component={TrafficJamRoutes} />
      <Route path="/" element={<Navigate to="/accidents" replace />} />
    </Routes>
  );
}

export default App;
