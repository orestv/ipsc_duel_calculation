import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css';

import * as $ from "jquery"
import React from "react";
import {createRoot} from "react-dom/client";

import App from "./components/app";


const root = createRoot(document.getElementById('reactContainer'))
root.render(<App/>)
// import {generatePairs, loadFromLocalStorage, saveToLocalStorage} from "./legacy/legacy";

// todo: participant list edits per class, category and range
// todo: send participant lists to the server
// todo: render participant lists per range
// todo: dynamic participant and duel count
// todo: download participation excel

// todo: parse participant list from practicarms into the edits

// $("#btnSaveToLocalStorage").on("click", saveToLocalStorage)
// $("#btnLoadFromLocalStorage").on("click", loadFromLocalStorage);
// $("#btnGeneragePairs").on("click", generatePairs);
//
// $(loadFromLocalStorage);
// $(function() {$("#container-result").hide()})
//
// $("#formParticipantLists textarea")
//     .on("change keyup paste", saveToLocalStorage)
//     .on("change keyup paste", generatePairs)


