'use client';

import React from 'react';
import Image from 'next/image';
import './FeaturesSection.css'; // Import the dedicated CSS file

// --- SVG ICONS ---
// These remain the same as they don't have external styling.
const ClockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);
const SyncIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"></path><path d="M21 21v-5h-5"></path>
  </svg>
);
const ChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 3v18h18"></path><path d="M18.7 8a5 5 0 0 0-7.4-1L9 10l-4 4"></path>
  </svg>
);
const MailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2"></rect><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
  </svg>
);

// --- STATIC DATA ---
const featureData = [
    {
        icon: <ClockIcon />,
        title: 'Task and Time Tracking',
        description: 'Create and log tasks with detailed descriptions. Track time in real time with start, pause, and stop options.',
    },
    {
        icon: <SyncIcon />,
        title: 'ACE Timesheet Integration',
        description: 'Seamlessly sync with the ACE timesheet app. Automatically populate timesheets from your task logs.',
    },
    {
        icon: <ChartIcon />,
        title: 'Performance Review Reports',
        description: 'Generate summary reports of your task activity and time logs. Export in CSV or Excel formats.',
    },
    {
        icon: <MailIcon />,
        title: 'Automated Supervisor Summaries',
        description: 'Send daily, weekly, or custom summaries to supervisors via Microsoft Teams or Outlook.',
    },
];

const companyLogos = [
    "Microsoft", "Google", "Apple", "Amazon", "Meta", "Tesla", "Netflix", "Spotify", "Salesforce"
];

// --- MAIN COMBINED COMPONENT ---
const FeaturesSection = () => {
  return (
    <>
      {/* --- TRUSTED BY SECTION (Integrated) --- */}
      <section className="trusted-by-section">
        <div className="container">
          <h2 className="trusted-by-heading">
            Trusted by the world's most innovative teams
          </h2>
          <div className="scrolling-logos-container">
            <ul className="scrolling-logos">
              {companyLogos.map((company, index) => (
                <li key={`${company}-${index}`}>
                  <span className="company-logo-text">{company}</span>
                </li>
              ))}
            </ul>
            {/* Duplicate for seamless loop */}
            <ul className="scrolling-logos" aria-hidden="true">
              {companyLogos.map((company, index) => (
                <li key={`${company}-${index}-clone`}>
                  <span className="company-logo-text">{company}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* --- FEATURES SECTION --- */}
      <section className="features-section">
        <div className="container">
          <div className="features-grid">
            {/* Left Side: Content */}
            <div className="features-content-left">
              <div className="features-heading-group">
                <p className="features-subtitle">Powerful Features</p>
                <h2 className="features-title">
                  Everything you need to track time effectively
                </h2>
                <p className="features-description">
                  Our features are designed to be simple, intuitive, and powerful, helping your team stay productive.
                </p>
              </div>
              <div className="features-list">
                {featureData.map((feature) => (
                  <div key={feature.title} className="feature-item">
                    <div className="feature-icon-wrapper">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="feature-item-title">{feature.title}</h3>
                      <p className="feature-item-description">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Side: Image */}
            <div className="features-image-right">
              <div className="image-background-gradients">
                <div className="gradient-1"></div>
                <div className="gradient-2"></div>
              </div>
              <div className="image-wrapper">
                <Image
                  src="/AL.png"
                  alt="A modern analytics dashboard UI with a central bar chart and floating project cards."
                  width={600}
                  height={450}
                  className="feature-image"
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
};

export default FeaturesSection;