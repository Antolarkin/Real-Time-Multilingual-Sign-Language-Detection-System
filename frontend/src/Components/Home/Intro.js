import React from "react";

function Intro() {
  return (
    <section id="intro" className="intro-section">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-10 text-center">
            <h2 className="section-title">
              We've Got <span className="highlight">What You Need!</span>
            </h2>
            <div className="section-divider">
              <div className="divider-line"></div>
              <div className="divider-icon">
                <i className="fas fa-hand-peace"></i>
              </div>
              <div className="divider-line"></div>
            </div>
            <p className="section-description">
              A comprehensive Indian Sign Language toolkit designed with both
              beauty and functionality in mind. Our minimalist interface houses
              powerful features that make working with ISL intuitive and
              effective.
              <span className="highlight-text">
                {" "}
                Everything you need is right here!
              </span>{" "}
              Dive into our diverse services and share your experience with our
              growing community.
            </p>

            <div className="intro-features">
              <div className="feature-item">
                <div className="feature-icon">
                  <i className="fas fa-magic"></i>
                </div>
                <span className="feature-text">Intuitive Design</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">
                  <i className="fas fa-bolt"></i>
                </div>
                <span className="feature-text">Lightning Fast</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">
                  <i className="fas fa-heart"></i>
                </div>
                <span className="feature-text">Community Focused</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Animated background elements */}
      <div className="intro-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
      </div>
    </section>
  );
}

export default Intro;
