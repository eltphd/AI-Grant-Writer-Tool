import React, { useState } from 'react';
import './NavigationComponent.css';

const NavigationComponent = ({ currentStep, onStepChange, user }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigationItems = [
    {
      id: 1,
      title: 'Projects',
      icon: '📁',
      description: 'View your grant projects'
    },
    {
      id: 2,
      title: 'Create Grant',
      icon: '✍️',
      description: 'Upload documents and write sections'
    },
    {
      id: 3,
      title: 'Chat',
      icon: '💬',
      description: 'AI-powered grant writing'
    },
    {
      id: 4,
      title: 'Export',
      icon: '📄',
      description: 'Review and export proposal'
    }
  ];

  const handleStepClick = (stepId) => {
    onStepChange(stepId);
    setIsMobileMenuOpen(false); // Close mobile menu after selection
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.reload();
  };

  const currentItem = navigationItems.find(item => item.id === currentStep);

  return (
    <div className="navigation-container">
      {/* Desktop Navigation */}
      <div className="navigation-desktop">
        <div className="navigation-header">
          <div className="nav-brand">
            <span className="nav-icon">📋</span>
            <div className="nav-title">
              <h1>GWAT</h1>
              <p>Grant Writing Assisted Toolkit</p>
            </div>
          </div>
          
          {user && (
            <div className="user-menu">
              <div className="user-info">
                <span className="user-avatar">👤</span>
                <span className="user-name">{user.name}</span>
              </div>
              <button className="logout-btn" onClick={handleLogout}>
                🚪
              </button>
            </div>
          )}
        </div>

        <nav className="navigation-menu">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${currentStep === item.id ? 'active' : ''}`}
              onClick={() => handleStepClick(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <div className="nav-content">
                <span className="nav-title">{item.title}</span>
                <span className="nav-description">{item.description}</span>
              </div>
              {currentStep === item.id && (
                <span className="nav-indicator"></span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Mobile Navigation */}
      <div className="navigation-mobile">
        <div className="mobile-header">
          <div className="mobile-brand">
            <span className="nav-icon">📋</span>
            <div className="nav-title">
              <h1>GWAT</h1>
            </div>
          </div>
          
          <button 
            className={`mobile-menu-btn ${isMobileMenuOpen ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>

        {/* Mobile Menu Overlay */}
        {isMobileMenuOpen && (
          <div className="mobile-menu-overlay" onClick={() => setIsMobileMenuOpen(false)}>
            <div className="mobile-menu" onClick={(e) => e.stopPropagation()}>
              <div className="mobile-menu-header">
                <h3>Menu</h3>
                <button 
                  className="mobile-close-btn"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  ✕
                </button>
              </div>
              
              <nav className="mobile-nav">
                {navigationItems.map((item) => (
                  <button
                    key={item.id}
                    className={`mobile-nav-item ${currentStep === item.id ? 'active' : ''}`}
                    onClick={() => handleStepClick(item.id)}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    <div className="nav-content">
                      <span className="nav-title">{item.title}</span>
                      <span className="nav-description">{item.description}</span>
                    </div>
                  </button>
                ))}
              </nav>
            </div>
          </div>
        )}

        {/* Mobile Current Step Indicator */}
        <div className="mobile-current-step">
          <span className="current-step-icon">{currentItem?.icon}</span>
          <span className="current-step-title">{currentItem?.title}</span>
        </div>
      </div>
    </div>
  );
};

export default NavigationComponent; 