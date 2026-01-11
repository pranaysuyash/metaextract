import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/coverage/**',
      '**/docs/**',
      '**/doc/**',
      '**/reports/**',
      '**/tmp/**',
      '**/test-data/**',
      '**/test_datasets/**',
      '**/test_images/**',
      '**/test_images_final/**',
      '**/tests/**',
      '**/__tests__/**',
      '**/scripts/**',
      '**/script/**',
      '**/server/extractor/**',
      '**/server/storage/**',
      '**/data/**',
      '**/attached_assets/**',
      '**/performance_reports/**',
      '**/validation_reports/**',
      '**/monitoring/**',
      '**/deployment/**',
      '**/replit/**',
      '**/tools/**',
      '**/*.test.ts',
      '**/*.test.tsx',
      'client/src/lib/a11y/**',
      'client/src/lib/adaptive-learning/**',
      'client/src/lib/shortcuts/**'
    ]
  },
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        },
        ecmaVersion: 2022,
        sourceType: 'module',
        project: './tsconfig.json'
      },
      globals: {
        console: 'readonly',
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        document: 'readonly',
        window: 'readonly',
        navigator: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        crypto: 'readonly',
        React: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': tseslint,
      'react': react,
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y
    },
    rules: {
      // TypeScript specific rules
      '@typescript-eslint/no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-empty-function': 'warn',

      // React specific rules
      'react/react-in-jsx-scope': 'off', // Not needed in React 17+
      'react/prop-types': 'off', // Using TypeScript for prop validation
      'react/display-name': 'warn',

      // Accessibility rules
      'jsx-a11y/alt-text': ['error', { 'elements': ['img'], 'img': ['Image'] }],
      'jsx-a11y/anchor-is-valid': ['error', {
        'components': ['Link'],
        'specialLink': ['hrefLeft', 'hrefRight'],
        'aspects': ['invalidHref', 'preferButton']
      }],
      'jsx-a11y/click-events-have-key-events': 'warn',
      'jsx-a11y/no-static-element-interactions': 'warn',

      // General rules
      'no-console': 'warn',
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'warn',
      'prefer-arrow-callback': 'error',
      'no-unused-vars': 'off', // Handled by TypeScript rule
      'no-undef': 'off' // Handled by TypeScript
    },
    settings: {
      react: {
        version: 'detect'
      }
    }
  },
  {
    files: ['server/**/*.ts'],
    rules: {
      'no-console': 'off' // Allow console in server code
    }
  },
  {
    files: ['**/*.js'],
    rules: {
      '@typescript-eslint/no-var-requires': 'off'
    }
  }
];
