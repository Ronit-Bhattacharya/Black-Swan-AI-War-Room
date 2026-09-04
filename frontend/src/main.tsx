import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
// @ts-expect-error CSS is handled by the bundler at runtime.
import "./styles.css";

ReactDOM.createRoot(
  document.getElementById("root")!,
).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
