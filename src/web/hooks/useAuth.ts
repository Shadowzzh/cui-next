import { useEffect } from 'react';

const AUTH_COOKIE_NAME = 'cui-auth-token';

/**
 * Get auth token from cookie
 */
export function getAuthToken(): string | null {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === AUTH_COOKIE_NAME) {
      return decodeURIComponent(value);
    }
  }
  return null;
}

/**
 * Set auth token in cookie with security flags
 */
export function setAuthToken(token: string): void {
  const expires = new Date();
  expires.setDate(expires.getDate() + 7); // 7 days expiration
  
  document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(token)}; expires=${expires.toUTCString()}; path=/; SameSite=Strict`;
}

/**
 * Extract token from URL fragment and store in cookie
 * Format: #token=xxxxx
 */
function extractTokenFromFragment(): string | null {
  const fragment = window.location.hash;
  if (!fragment.startsWith('#token=')) {
    return null;
  }

  const token = fragment.substring(7); // Remove '#token='
  if (token.length !== 32 || !/^[a-f0-9]+$/.test(token)) {
    console.warn('Invalid token format in URL fragment');
    return null;
  }

  return token;
}

/**
 * Clear URL fragment
 */
function clearFragment(): void {
  if (window.history && window.history.replaceState) {
    // Remove fragment without affecting browser history
    window.history.replaceState(null, '', window.location.pathname + window.location.search);
  } else {
    // Fallback for older browsers
    window.location.hash = '';
  }
}

/**
 * Initialize auth: extract token from URL fragment if present
 * This runs immediately when the module is imported (before React renders)
 */
function initializeAuth(): void {
  // Only run in browser environment
  if (typeof window === 'undefined') return;

  const fragmentToken = extractTokenFromFragment();

  if (fragmentToken) {
    // Store token in cookie
    setAuthToken(fragmentToken);

    // Clear fragment from URL
    clearFragment();

    console.log('Authentication token stored successfully');
  }
}

// Run initialization immediately when module loads
initializeAuth();

/**
 * Hook for handling authentication token extraction and storage
 * Now just a no-op since initialization happens at module load
 */
export function useAuth(): void {
  // Token extraction now happens synchronously at module load
  // This hook is kept for backward compatibility
  useEffect(() => {
    // Nothing to do here anymore
  }, []);
}