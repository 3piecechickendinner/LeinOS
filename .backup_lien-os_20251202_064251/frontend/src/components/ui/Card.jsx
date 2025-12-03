import React from 'react';

export function Card({ children, className = '', ...props }) {
  return (
    <div
      className={`bg-white border border-slate-200 rounded-lg ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '', ...props }) {
  return (
    <div
      className={`px-4 py-3 border-b border-slate-200 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '', ...props }) {
  return (
    <h3
      className={`text-sm font-semibold text-slate-900 ${className}`}
      {...props}
    >
      {children}
    </h3>
  );
}

export function CardContent({ children, className = '', ...props }) {
  return (
    <div className={`px-4 py-3 ${className}`} {...props}>
      {children}
    </div>
  );
}

export default Card;
