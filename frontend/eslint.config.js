/**
 * ESLint v9 flat config pour le frontend Plume Astrale.
 *
 * Audit (2026-10-30 · Nao) phase 2 : objectif = catcher les VRAIS bugs
 * (hooks, variables non définies, dépendances useEffect) sans noyer le dev
 * sous les règles stylistiques. CRA 5 est deprecated, donc pas de
 * eslint-config-react-app ici.
 *
 * Les tests Jest / scripts build sont ignorés. On applique les règles
 * recommandées de @eslint/js + eslint-plugin-react + eslint-plugin-react-hooks.
 */
const js = require('@eslint/js');
const globals = require('globals');
const reactPlugin = require('eslint-plugin-react');
const reactHooks = require('eslint-plugin-react-hooks');

module.exports = [
  js.configs.recommended,
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.jest,
        process: 'readonly',
      },
    },
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooks,
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      // ─── React fondamentaux ───
      'react/jsx-uses-react': 'off',           // JSX transform auto
      'react/react-in-jsx-scope': 'off',       // React import pas requis en 17+
      'react/jsx-uses-vars': 'error',          // flag les vars JSX inutilisées
      'react/jsx-no-undef': 'error',           // flag les composants inconnus
      'react/no-unescaped-entities': 'off',    // apostrophes FR partout
      'react/prop-types': 'off',               // pas de PropTypes dans ce code
      'react/display-name': 'off',

      // ─── Hooks (critiques) ───
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',

      // ─── Qualité code ───
      'no-unused-vars': ['warn', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
      }],
      'no-undef': 'error',
      'no-console': 'off',
      'no-empty': ['warn', { allowEmptyCatch: true }],
      'no-constant-condition': ['warn', { checkLoops: false }],
      'no-useless-escape': 'warn',
      'no-case-declarations': 'off',
      'no-prototype-builtins': 'off',
      'no-mixed-spaces-and-tabs': 'warn',
    },
  },
  {
    // Scripts Node (build, prerender, config)
    files: ['scripts/**/*.js', 'craco.config.js', '*.config.js'],
    languageOptions: {
      globals: { ...globals.node },
      sourceType: 'commonjs',
    },
  },
  {
    // Tests
    files: ['src/**/*.{test,spec}.{js,jsx}'],
    languageOptions: {
      globals: { ...globals.jest, ...globals.node },
    },
    rules: {
      'no-unused-vars': 'off',
    },
  },
  {
    ignores: [
      'build/**',
      'node_modules/**',
      'public/**',
      'coverage/**',
      'test-results/**',
      'playwright-report/**',
      // Fichiers legacy ou tiers injectés
      'src/serviceWorker.js',
    ],
  },
];
