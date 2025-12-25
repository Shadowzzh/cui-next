import { Logger } from '../services/logger.js';

export interface ServerStartupOptions {
  host: string;
  port: number;
  logger: Logger;
}

/**
 * Display server startup information with rocket emoji and open browser
 */
export function displayServerStartup(options: ServerStartupOptions): void {
  const { host, port, logger } = options;
  const serverUrl = `http://${host}:${port}`;

  logger.info(`🚀 Server listening on ${serverUrl}`);
  logger.info('🔓 Direct access - no authentication required');
}
