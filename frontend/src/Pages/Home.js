import React from "react";
import "../css/Home.css";
import "font-awesome/css/font-awesome.min.css";
import Services from "../Components/Home/Services";
import Intro from "../Components/Home/Intro";
import Masthead from "../Components/Home/Masthead";

function Home() {
  return (
    <div>

      <Masthead />

      <Intro />
      
      <Services />
      
    </div>
  );
}

export default Home;
