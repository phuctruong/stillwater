---
name: styleguide-first
description: "Design tokens and accessibility-first architecture."
---

# Styleguide First Protocol

1. **Tokens Over Hex**: Never use hardcoded colors (e.g. `#fff`) outside of `:root` CSS variables.
2. **Accessibility**: All interactive elements must have semantic tags (e.g. `<button>`, not `<div onclick="...">`).
3. **PHUC Architecture**: One `site.css`, one `solace.js`. No inline styles or inline scripts.
