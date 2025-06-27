// Auth0 configuration and utilities
export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || 'demo.auth0.com',
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || 'demo-client-id',
  redirectUri: window.location.origin,
  audience: import.meta.env.VITE_AUTH0_AUDIENCE,
};

// Mock auth functions for demo
export const mockAuth = {
  isAuthenticated: true,
  user: {
    name: 'Demo User',
    email: 'demo@example.com',
    picture: 'https://via.placeholder.com/40',
  },
  
  login: () => {
    console.log('Mock login');
    localStorage.setItem('auth_token', 'mock-jwt-token');
  },
  
  logout: () => {
    console.log('Mock logout');
    localStorage.removeItem('auth_token');
  },
  
  getToken: () => {
    return localStorage.getItem('auth_token') || 'mock-jwt-token';
  },
};

export default mockAuth;