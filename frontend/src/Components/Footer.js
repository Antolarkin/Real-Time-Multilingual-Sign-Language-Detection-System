import React from "react";
import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="page-footer font-small unique-color-dark mt-5">
      <div
        className="container-fluid text-white pt-3"
        style={{ backgroundColor: "rgba(33,37,41,1)" }}
      >
        <div className="container text-md-left mt-5">
          <div className="row mt-3">
            <div className="col-md-6 mx-auto mb-4">
              <h6 className="text-uppercase font-weight-bold">SignLingua</h6>
              <hr
                className="deep-purple accent-2 mb-4 mt-0 d-inline-block mx-auto"
                style={{ width: "60px" }}
              />
              <p className="footer-text">
                A comprehensive toolkit containing various features related to
                Indian Sign Language.
              </p>
            </div>
            <div className="col-md-6 mx-auto mb-4">
              <h6 className="text-uppercase font-weight-bold">Services</h6>
              <hr
                className="deep-purple accent-2 mb-4 mt-0 d-inline-block mx-auto"
                style={{ width: "60px" }}
              />
              <p>
                <Link to="/sign-kit/convert" className="footer-link">
                  3D Avatar Converter
                </Link>
              </p>
              <p>
                <Link to="/sign-kit/learn-sign" className="footer-link">
                  Learn Sign Language
                </Link>
              </p>
              <p>
                <Link to="/sign-kit/detect" className="footer-link">
                  Sign Detection Practice
                </Link>
              </p>
            </div>
          </div>
        </div>

        <div className="footer-copyright text-center py-3">
          © {new Date().getFullYear()} Copyright
        </div>
      </div>
    </footer>
  );
}

export default Footer;
