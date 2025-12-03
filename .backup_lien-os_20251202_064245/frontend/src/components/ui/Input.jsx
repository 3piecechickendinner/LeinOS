import React from 'react';

export function Input({
  label,
  error,
  className = '',
  id,
  ...props
}) {
  const inputId = id || props.name;

  return (
    <div className="space-y-1">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-xs font-medium text-slate-600"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`
          w-full px-3 py-2 text-sm text-slate-900
          bg-white border border-slate-300 rounded-md
          placeholder:text-slate-400
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed
          ${error ? 'border-red-500' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}
    </div>
  );
}

export function Select({
  label,
  error,
  options = [],
  className = '',
  id,
  ...props
}) {
  const selectId = id || props.name;

  return (
    <div className="space-y-1">
      {label && (
        <label
          htmlFor={selectId}
          className="block text-xs font-medium text-slate-600"
        >
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`
          w-full px-3 py-2 text-sm text-slate-900
          bg-white border border-slate-300 rounded-md
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed
          ${error ? 'border-red-500' : ''}
          ${className}
        `}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}
    </div>
  );
}

export default Input;
