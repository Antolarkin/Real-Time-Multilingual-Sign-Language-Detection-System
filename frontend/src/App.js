import "./App.css";
import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import Convert from "./Pages/Convert";
import Home from "./Pages/Home";
import LearnSign from "./Pages/LearnSign";
import Video from "./Pages/Video";
import Navbar from "./Components/Navbar";
import CreateVideo from "./Pages/CreateVideo";
import Footer from "./Components/Footer";
import Videos from "./Pages/Videos";
import Feedback from "./Pages/Feedback";
import SignLanguageDetector from "./Pages/Sign";
import Detect from "./Pages/Detect";
import LoginPage from "./Pages/Login";
import SignupPage from "./Pages/SignUp";
import Games from "./Pages/Games";

function AppContent() {
  const location = useLocation();
  const hideNavbar =
    location.pathname === "/" || location.pathname === "/signup";

  return (
    <div>
      {!hideNavbar && <Navbar />}
      <Routes>
        <Route exact path="/sign-kit/home" element={<Home />} />
        <Route exact path="/sign-kit/convert" element={<Convert />} />
        <Route exact path="/sign-kit/learn-sign" element={<LearnSign />} />
        <Route exact path="/sign-kit/all-videos" element={<Videos />} />
        <Route exact path="/sign-kit/video/:videoId" element={<Video />} />
        <Route exact path="/sign-kit/create-video" element={<CreateVideo />} />
        <Route exact path="/sign-kit/feedback" element={<Feedback />} />
        <Route exact path="/sign-kit/detect" element={<Detect />} />
        <Route exact path="/sign-kit/games" element={<Games />} />
        <Route exact path="/signup" element={<SignupPage />} />
        <Route path="*" element={<LoginPage />} />
      </Routes>
      {!hideNavbar && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
