import React from 'react';
import ReactDOM from "react-dom";
import { createRoot } from 'react-dom/client';
import * as JsCookie from "js-cookie"; // generated
export { DashboardCharts } from './dashboard/dashboard-charts';
import App from './zonprep_app/App';

// pass-through for Cookies API
export const Cookies = JsCookie.default;

console.log('App.js loaded');

const root = createRoot(document.getElementById('front-end-react-app'));

root.render(<App />);