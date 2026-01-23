/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/client', '<rootDir>/server', '<rootDir>/shared'],
  testMatch: [
    '**/__tests__/**/*.{js,jsx,ts,tsx}',
    '**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  transform: {
    '^.+\\.(ts|tsx)$': [
      'ts-jest',
      {
        useESM: true,
        tsconfig: {
          jsx: 'react-jsx',
          esModuleInterop: true,
          module: 'ESNext',
          moduleResolution: 'node',
          target: 'ES2022',
          strict: true,
          skipLibCheck: true,
          isolatedModules: true,
        },
      },
    ],
    '^.+\\.(js|jsx)$': [
      'babel-jest',
      {
        presets: [
          ['@babel/preset-env', { targets: { node: 'current' } }],
          ['@babel/preset-react', { runtime: 'automatic' }],
        ],
      },
    ],
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/client/src/$1',
    '^@shared/(.*)$': '<rootDir>/shared/$1',
    '^file-type$': '<rootDir>/tests/mocks/file-type.cjs',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts', '@testing-library/jest-dom'],
  globalTeardown: '<rootDir>/tests/global-teardown.js',
  collectCoverageFrom: [
    'client/src/**/*.{ts,tsx}',
    '!client/src/main.tsx',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 5,
      functions: 5,
      lines: 5,
      statements: 5,
    },
  },
  coverageReporters: ['text', 'lcov', 'html'],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    // Obsolete tests (deprecated tier-based pricing system)
    'subscription\\.property\\.test\\.ts$',
    'pricing\\.property\\.test\\.ts$',
    // Env-gated tests (require RUN_PERF_TESTS=1 or RUN_DB_INIT_DEBUG=1)
    'performance-load\\.test\\.ts$',
    'db-init-debug\\.integration\\.test\\.ts$',
  ],
  transformIgnorePatterns: ['/node_modules/(?!( @tanstack/react-query|uuid)/)'],
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
  verbose: true,
  // Run integration tests in separate processes to avoid port conflicts
  maxWorkers: 1,
};
