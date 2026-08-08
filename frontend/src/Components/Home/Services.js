import React from "react";
import { Link } from "react-router-dom";
import imgConvert from "../../Assets/convert.png";
import imgLearnSign from "../../Assets/learn-sign.jpg";
import imgVideos from "../../Assets/videos.png";

function Services() {
  const services = [
    {
      title: "3D Avatar Converter",
      description:
        "Our 3D avatar converts your spoken or written sentences into Indian Sign Language hand signs in real-time. Speak into your mic or type your text and watch the avatar demonstrate the signs.",
      image: imgConvert,
      link: "/sign-kit/convert",
    },
    {
      title: "Learn Sign Language",
      description:
        "Interactive learning platform where you can click on words and characters to see our 3D avatar demonstrate the corresponding signs. Build your ISL vocabulary at your own pace.",
      image: imgLearnSign,
      link: "/sign-kit/learn-sign",
    },
    {
      title: "Sign Detection Practice",
      description:
        "Practice your own hand signs with our ML-powered detection system. The system recognizes your signs and displays the corresponding words/characters, allowing you to frame complete sentences.",
      image: imgVideos,
      link: "/sign-kit/detect",
    },
  ];

  return (
    <section id="services" className="services-section">
      <div className="container">
        <div className="row">
          <div className="col-12 text-center section-header">
            <h2 className="section-title">
              Our <span className="highlight">Services</span>
            </h2>
            <div className="section-divider">
              <div className="divider-line"></div>
              <div className="divider-icon">
                <i className="fas fa-hands"></i>
              </div>
              <div className="divider-line"></div>
            </div>
            <p className="section-description">
              A comprehensive Indian Sign Language toolkit designed to empower
              communication. Explore our carefully crafted features that make
              working with ISL intuitive and enjoyable. We've wrapped everything
              you need in one beautiful package!
            </p>
          </div>
        </div>

        <div className="row services-grid">
          {services.map((service, index) => (
            <div className="col-lg-4 col-md-6 mb-4" key={index}>
              <div className="service-card">
                <div className="card-image-container">
                  <img
                    src={service.image}
                    alt={service.title}
                    className="card-image"
                  />
                  <div className="image-overlay"></div>
                </div>
                <div className="card-content">
                  <h3 className="card-title">{service.title}</h3>
                  <p className="card-text">{service.description}</p>
                  <Link to={service.link} className="service-button">
                    Explore Now <i className="fas fa-arrow-right ml-2"></i>
                  </Link>
                </div>
                <div className="card-corner">
                  <span>0{index + 1}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Services;
