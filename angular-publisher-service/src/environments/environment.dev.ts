function resolveApiHost(): string {
  if (typeof window === 'undefined') {
    return '127.0.0.1';
  }
  const hostname = window.location.hostname;
  return hostname === 'angular-publisher-service' ? 'spring-publisher-service' : hostname;
}

export const environment = {
  production: false,
  apiBaseUrl: `http://${resolveApiHost()}:8080/api/v1`
};