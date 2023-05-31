import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css';

import React from "react";
import {createRoot} from "react-dom/client";

import App from "./components/app";


const root = createRoot(document.getElementById('reactContainer'))
root.render(<App/>)
