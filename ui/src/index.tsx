import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css';

import React from "react";
import * as ReactDOM from "react-dom/client";

import {createBrowserRouter, RouterProvider} from 'react-router-dom';

import App from "./components/app";
import Root from "./components/root";
import Container from "react-bootstrap/Container";
import MatchList from "./components/matches/match_list";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root/>,
    children: [
      {
        path: "duels",
        element: <App/>
      },
      {
        path: "matches",
        element: <MatchList/>
      }
    ]
  },
]);

ReactDOM.createRoot(document.getElementById("reactContainer")).render(
  // <React.StrictMode>
    <RouterProvider router={router} />
  // </React.StrictMode>
);

// const root = createRoot(document.getElementById('reactContainer'))
// root.render(<App/>)
