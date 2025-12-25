import { createLogger } from './services/logger.js';

export interface CLIConfig {
  port?: number;
  host?: string;
  token?: string;
  skipAuthToken?: boolean;
}

/**
 * Parse command line arguments and environment variables
 * Priority: CLI args > Environment variables > Config file
 */
export function parseArgs(argv: string[]): CLIConfig {
  const logger = createLogger('CLIParser');
  const args = argv.slice(2);
  const config: CLIConfig = {};

  // Step 1: Read from environment variables (lowest priority)
  if (process.env.PORT) {
    const portValue = parseInt(process.env.PORT, 10);
    if (!isNaN(portValue) && portValue > 0 && portValue <= 65535) {
      config.port = portValue;
      logger.debug(`Loaded port from PORT environment variable: ${portValue}`);
    } else {
      logger.warn(`Invalid PORT environment variable: ${process.env.PORT}`);
    }
  }

  if (process.env.HOST) {
    config.host = process.env.HOST;
    logger.debug(`Loaded host from HOST environment variable: ${process.env.HOST}`);
  }

  if (process.env.AUTH_TOKEN) {
    config.token = process.env.AUTH_TOKEN;
    logger.debug('Loaded auth token from AUTH_TOKEN environment variable');
  }

  if (process.env.SKIP_AUTH_TOKEN === 'true' || process.env.SKIP_AUTH_TOKEN === '1') {
    config.skipAuthToken = true;
    logger.debug('Auth token checking disabled via SKIP_AUTH_TOKEN environment variable');
  }

  // Step 2: Override with command line arguments (highest priority)
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--port':
        if (i + 1 < args.length) {
          const portValue = parseInt(args[++i], 10);
          if (!isNaN(portValue) && portValue > 0 && portValue <= 65535) {
            config.port = portValue;
          } else {
            logger.error(`Invalid port value: ${args[i]}`);
            process.exit(1);
          }
        } else {
          logger.error('--port requires a value');
          process.exit(1);
        }
        break;

      case '--host':
        if (i + 1 < args.length) {
          config.host = args[++i];
        } else {
          logger.error('--host requires a value');
          process.exit(1);
        }
        break;

      case '--token':
        if (i + 1 < args.length) {
          config.token = args[++i];
        } else {
          logger.error('--token requires a value');
          process.exit(1);
        }
        break;

      case '--skip-auth-token':
        config.skipAuthToken = true;
        break;

      default:
        logger.error(`Unknown argument: ${arg}`);
        logger.info(
          'Usage: cui-server [--port <number>] [--host <string>] [--token <string>] [--skip-auth-token]'
        );
        logger.info('Environment variables: PORT, HOST, AUTH_TOKEN, SKIP_AUTH_TOKEN');
        process.exit(1);
    }
  }

  return config;
}
