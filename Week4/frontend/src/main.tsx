import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import App from "./App";
import "@radix-ui/themes/styles.css";
import "./main.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="iris" grayColor="slate">
      <App />
    </Theme>
  </React.StrictMode>
);
