import React from 'react';

const GlassCard = ({ children, title, style = {} }) => {
  return (
    <div className="glass-card" style={style}>
      {title && (
        <h2 style={{
          fontSize: '14px',
          fontWeight: '600',
          marginBottom: '20px',
          color: 'var(--text-primary)',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          {title}
        </h2>
      )}
      {children}
    </div>
  );
};

export default GlassCard;
