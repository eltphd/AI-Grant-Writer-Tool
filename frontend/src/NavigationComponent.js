import React from 'react';
import './NavigationComponent.css';

const NavigationComponent = ({ currentStep, onStepChange, user }) => {
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
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.reload();
  };

  return (
    <div className="navigation-container">
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
  );
};

export default NavigationComponent; 