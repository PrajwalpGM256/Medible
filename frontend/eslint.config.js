import antfu from '@antfu/eslint-config'

export default antfu({
  // Frameworks
  vue: true,
  typescript: true,

  // Formatting (uses ESLint Stylistic instead of Prettier)
  formatters: {
    css: true,
    html: true,
    markdown: true,
  },

  // Disable UnoCSS (you use Tailwind)
  unocss: false,

  // Style preferences
  stylistic: {
    indent: 2,
    quotes: 'single',
    semi: false,
  },

  // Ignore patterns
  ignores: [
    'dist/',
    'node_modules/',
    'src/components/ui/', // shadcn-vue generated components
    '*.min.js',
  ],

  // Custom rules for Medible
  rules: {
    // Code quality (adapted from professional config)
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'error',
    'no-eval': 'error',
    'prefer-const': 'warn',
    'no-param-reassign': 'error',
    'max-statements-per-line': ['error', { max: 1 }],

    // Component & function size limits (your principles!)
    'max-lines': ['warn', {
      max: 200, // Components under 200 lines
      skipBlankLines: true,
      skipComments: true,
    }],
    'max-lines-per-function': ['warn', {
      max: 50, // Functions should be focused
      skipBlankLines: true,
      skipComments: true,
      IIFEs: true,
    }],
    'max-statements': ['warn', 25], // Max statements per function
    'max-depth': ['warn', 4], // Max nesting depth
    'max-params': ['warn', 4], // Max function parameters
    'complexity': ['warn', 15], // Cyclomatic complexity limit

    // Vue-specific
    'vue/no-static-inline-styles': 'warn', // Your principle: no inline styles!
    'vue/component-tags-order': ['warn', {
      order: ['script', 'template', 'style'],
    }],
    'vue/block-lang': ['warn', {
      script: { lang: 'ts' },
    }],
    'vue/define-emits-declaration': ['warn', 'type-based'],
    'vue/define-props-declaration': ['warn', 'type-based'],
    'vue/no-empty-component-block': 'warn',
    'vue/padding-line-between-blocks': 'warn',
    'vue/prefer-true-attribute-shorthand': 'warn',
    'vue/multi-word-component-names': 'off', // Allow single-word view names

    // TypeScript
    'ts/no-unused-vars': ['warn', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    'ts/no-explicit-any': 'warn',

    // Relaxed rules for practicality
    'antfu/if-newline': 'off',
    'style/brace-style': ['warn', '1tbs', { allowSingleLine: true }],
    'node/prefer-global/process': 'off',
  },
})