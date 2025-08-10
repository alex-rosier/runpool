# CSS Architecture Documentation

## Overview
The CSS has been reorganized into a modular structure for better maintainability and organization. Instead of one large `styles.css` file, styles are now separated into logical modules.

## File Structure

### Main Entry Point
- **`main.css`** - Main CSS file that imports all modules using `@import` statements

### Core Modules
- **`base.css`** - Global styles, resets, common utilities, and shared components
- **`auth.css`** - Authentication-related styles (login, register, password reset)
- **`profile.css`** - Profile page and user management styles
- **`game.css`** - Game creation, editing, and management styles
- **`scorecard.css`** - Scorecard display and table styles
- **`components.css`** - Reusable UI components (modals, buttons, forms)

## Benefits of This Structure

1. **Easier Maintenance** - Find and modify styles for specific features quickly
2. **Better Organization** - Related styles are grouped together logically
3. **Reduced Merge Conflicts** - Team members can work on different modules simultaneously
4. **Improved Readability** - Smaller, focused files are easier to understand
5. **Better Debugging** - Isolate issues to specific feature areas

## How to Use

### For Development
1. **Adding New Styles**: Create a new CSS file for the feature and add an `@import` statement in `main.css`
2. **Modifying Existing Styles**: Find the appropriate module file and make changes there
3. **Global Changes**: Use `base.css` for site-wide modifications

### File Naming Convention
- Use descriptive names that indicate the purpose (e.g., `auth.css`, `game.css`)
- Keep names short but clear
- Use lowercase with hyphens for multi-word names

### Import Order
The import order in `main.css` matters:
1. `base.css` first (global styles and resets)
2. Feature-specific modules (auth, profile, game, etc.)
3. `components.css` last (reusable components that may override base styles)

## Migration Notes

- **Old File**: `styles.css` (can be deleted after confirming new structure works)
- **New Entry Point**: `main.css` (already updated in `base.html`)
- **All Existing Styles**: Preserved and organized into appropriate modules

## Best Practices

1. **Keep Modules Focused**: Each file should handle one specific area of functionality
2. **Avoid Duplication**: Use `base.css` for shared styles across multiple pages
3. **Consistent Naming**: Follow existing naming conventions for CSS classes
4. **Responsive Design**: Include media queries within each module as needed
5. **Documentation**: Add comments to explain complex CSS rules or business logic

## Troubleshooting

### Styles Not Loading
- Check that `main.css` is properly linked in your HTML templates
- Verify all `@import` statements are correct
- Check browser console for CSS loading errors

### Missing Styles
- Ensure the appropriate module file exists
- Check that the `@import` statement is added to `main.css`
- Verify the CSS file path is correct

### Performance Considerations
- CSS imports are processed sequentially, so order matters
- Consider using a CSS bundler for production to combine all files
- Monitor file sizes to ensure modules don't become too large

## Future Enhancements

Consider implementing:
- CSS preprocessors (Sass/SCSS) for better organization
- CSS-in-JS for component-specific styling
- CSS custom properties for consistent theming
- Automated CSS optimization and minification
