import { defineConfig } from "eslint/config";
import pluginSecurity from "eslint-plugin-security";

export default defineConfig([
  {
    files: ["**/*.js"],
    plugins: {
      security: pluginSecurity,
    },
    rules: {
      "security/detect-eval-with-expression": "error",
      "security/detect-unsafe-regex": "error",
    },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: {
        document: "readonly",
        alert: "readonly",
      },
    },
  },
]);