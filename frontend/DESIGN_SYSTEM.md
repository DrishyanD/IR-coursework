# Frontend Design System

## Visual direction

Academic research platform / research intelligence product.

Avoid:

- generic admin-dashboard appearance
- excessive gradients
- fake statistics
- decorative controls with no backend behavior
- unnecessary animation
- overly dense cards

Prefer:

- neutral backgrounds
- strong typography
- restrained accent color
- generous spacing
- clear hierarchy
- visible IR evidence
- accessible interaction

## Core tokens

CSS variables are defined in:

```text
src/styles/index.css
```

Primary tokens:

```text
--background
--surface
--surface-muted
--ink
--text-muted
--text-faint
--border
--border-strong
--accent
--accent-soft
```

## Component conventions

```text
Container   maximum-width page wrapper
Card        primary surface
Button      primary/secondary/ghost actions
Badge       low-emphasis metadata
SearchBar   global ranked-search entry point
```

## Accessibility

- semantic landmarks
- keyboard navigation
- visible focus
- skip link
- live route announcement
- reduced-motion support
- screen-reader labels
- print-friendly evidence views
