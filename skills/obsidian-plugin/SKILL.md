---
name: obsidian-plugin
description: Build and edit Obsidian plugins using TypeScript and the Obsidian API. Supports plugin development, feature implementation, and publishing workflows.
---

# Obsidian Plugin Development Skill

## Overview
This skill enables Claude to build and edit Obsidian plugins using TypeScript. Obsidian plugins extend the functionality of the Obsidian note-taking application through a well-defined API.

## When to Use This Skill
Use this skill when:
- Creating a new Obsidian plugin from scratch
- Modifying or debugging existing Obsidian plugins
- Adding features to Obsidian (commands, ribbon icons, settings, views, etc.)
- Working with the Obsidian API (vault, workspace, metadata cache, etc.)
- Setting up plugin development environments
- Preparing plugins for publication

## Core Concepts

### Plugin Architecture
Obsidian plugins are built on a component-based architecture:
- Plugins extend the `Plugin` class from the Obsidian API
- Lifecycle is managed through `onload()` and `onunload()` methods
- All registrations (commands, events, views) are automatically cleaned up on unload
- Access to Obsidian functionality through `this.app` property

### Required Files
Every Obsidian plugin requires these files:
1. **manifest.json** - Plugin metadata and version information
2. **main.ts** - TypeScript entry point with plugin class
3. **main.js** - Compiled JavaScript (generated from main.ts)
4. **package.json** - npm dependencies
5. **tsconfig.json** - TypeScript configuration
6. **esbuild.config.mjs** - Build configuration (or similar bundler config)

Optional files:
- **styles.css** - Custom CSS for plugin UI
- **versions.json** - Version compatibility tracking
- **README.md** - Documentation

## Plugin Structure

### Basic Plugin Template
```typescript
import { Plugin, Notice } from 'obsidian';

export default class MyPlugin extends Plugin {
    async onload() {
        console.log('Loading plugin');
        
        // Add ribbon icon
        this.addRibbonIcon('dice', 'My Plugin', () => {
            new Notice('Plugin activated!');
        });
        
        // Add command
        this.addCommand({
            id: 'my-command',
            name: 'Execute My Command',
            callback: () => {
                new Notice('Command executed!');
            }
        });
    }
    
    onunload() {
        console.log('Unloading plugin');
    }
}
```

### Manifest.json Structure
```json
{
    "id": "plugin-id",
    "name": "Plugin Name",
    "version": "1.0.0",
    "minAppVersion": "0.15.0",
    "description": "Plugin description",
    "author": "Author Name",
    "authorUrl": "https://example.com",
    "fundingUrl": "https://buymeacoffee.com/username",
    "isDesktopOnly": false
}
```

Required fields:
- `id`: Unique identifier (lowercase, hyphens, no spaces)
- `name`: Display name
- `version`: Semantic version (e.g., "1.0.0")
- `minAppVersion`: Minimum Obsidian version required
- `description`: Brief description
- `author`: Author name

Optional fields:
- `authorUrl`: Author's website
- `fundingUrl`: Donation/support link
- `isDesktopOnly`: Set to true if plugin uses NodeJS/Electron APIs

## Development Workflow

### Initial Setup
1. Clone or use the sample plugin template from: https://github.com/obsidianmd/obsidian-sample-plugin
2. Install dependencies: `npm install`
3. Start development build: `npm run dev` (watches for changes and auto-compiles)

### Development Process
1. Make changes to `main.ts` or create new `.ts` files
2. Files automatically compile to `main.js` (if using `npm run dev`)
3. Copy `main.js`, `manifest.json`, and `styles.css` to test vault:
   `<vault>/.obsidian/plugins/<plugin-id>/`
4. Reload Obsidian (or restart) to test changes
5. Enable plugin in Settings → Community Plugins

### Building for Production
```bash
npm run build
```
This creates an optimized `main.js` file ready for distribution.

## Common Plugin Features

### 1. Commands
```typescript
this.addCommand({
    id: 'unique-command-id',
    name: 'Command Name',
    callback: () => {
        // Execute command
    }
});

// Command with editor context
this.addCommand({
    id: 'editor-command',
    name: 'Editor Command',
    editorCallback: (editor, view) => {
        const selectedText = editor.getSelection();
        editor.replaceSelection(selectedText.toUpperCase());
    }
});

// Conditional command (only available when conditions met)
this.addCommand({
    id: 'conditional-command',
    name: 'Conditional Command',
    checkCallback: (checking) => {
        const canRun = this.someCondition();
        if (checking) return canRun;
        if (canRun) {
            // Execute command
        }
        return true;
    }
});
```

### 2. Ribbon Icons
```typescript
this.addRibbonIcon('icon-name', 'Tooltip text', (evt) => {
    // Icon clicked
    new Notice('Ribbon icon clicked!');
});
```

Available icons can be found at: https://lucide.dev/

### 3. Settings Tab
```typescript
import { App, PluginSettingTab, Setting } from 'obsidian';

interface MyPluginSettings {
    mySetting: string;
}

const DEFAULT_SETTINGS: MyPluginSettings = {
    mySetting: 'default'
}

export default class MyPlugin extends Plugin {
    settings: MyPluginSettings;
    
    async onload() {
        await this.loadSettings();
        this.addSettingTab(new MySettingTab(this.app, this));
    }
    
    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }
    
    async saveSettings() {
        await this.saveData(this.settings);
    }
}

class MySettingTab extends PluginSettingTab {
    plugin: MyPlugin;
    
    constructor(app: App, plugin: MyPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }
    
    display(): void {
        const {containerEl} = this;
        containerEl.empty();
        
        new Setting(containerEl)
            .setName('Setting name')
            .setDesc('Setting description')
            .addText(text => text
                .setPlaceholder('Enter value')
                .setValue(this.plugin.settings.mySetting)
                .onChange(async (value) => {
                    this.plugin.settings.mySetting = value;
                    await this.plugin.saveSettings();
                }));
    }
}
```

### 4. Modals
```typescript
import { Modal } from 'obsidian';

class MyModal extends Modal {
    onOpen() {
        const {contentEl} = this;
        contentEl.setText('Modal content!');
    }
    
    onClose() {
        const {contentEl} = this;
        contentEl.empty();
    }
}

// Open modal
new MyModal(this.app).open();
```

### 5. Event Handling
```typescript
// Register DOM event (auto-cleanup on unload)
this.registerDomEvent(document, 'click', (evt) => {
    console.log('Document clicked');
});

// Register Obsidian event
this.registerEvent(
    this.app.workspace.on('file-open', (file) => {
        console.log('File opened:', file);
    })
);

// Register interval (auto-cleanup on unload)
this.registerInterval(
    window.setInterval(() => {
        console.log('Interval tick');
    }, 5000)
);
```

### 6. Working with Files
```typescript
// Get active file
const file = this.app.workspace.getActiveFile();

// Read file content
if (file) {
    const content = await this.app.vault.read(file);
}

// Modify file
if (file) {
    await this.app.vault.modify(file, 'New content');
}

// Create file
await this.app.vault.create('path/to/file.md', 'Content');

// Get all markdown files
const files = this.app.vault.getMarkdownFiles();

// Get metadata cache
const cache = this.app.metadataCache.getFileCache(file);
```

### 7. Working with Editor
```typescript
// Get active editor
const editor = this.app.workspace.activeEditor?.editor;

if (editor) {
    // Get selection
    const selection = editor.getSelection();
    
    // Replace selection
    editor.replaceSelection('New text');
    
    // Get cursor position
    const cursor = editor.getCursor();
    
    // Insert text at cursor
    editor.replaceRange('Inserted text', cursor);
    
    // Get line
    const line = editor.getLine(cursor.line);
}
```

### 8. Views and Leaves
```typescript
import { ItemView, WorkspaceLeaf } from 'obsidian';

const VIEW_TYPE = 'my-custom-view';

class MyCustomView extends ItemView {
    getViewType() {
        return VIEW_TYPE;
    }
    
    getDisplayText() {
        return 'My Custom View';
    }
    
    async onOpen() {
        const container = this.containerEl.children[1];
        container.empty();
        container.createEl('h4', { text: 'My Custom View' });
    }
    
    async onClose() {
        // Cleanup if needed
    }
}

// In plugin's onload()
this.registerView(
    VIEW_TYPE,
    (leaf) => new MyCustomView(leaf)
);

// Open view
this.app.workspace.getRightLeaf(false).setViewState({
    type: VIEW_TYPE,
    active: true,
});
```

## Package.json Configuration
```json
{
    "name": "obsidian-plugin-name",
    "version": "1.0.0",
    "description": "Plugin description",
    "main": "main.js",
    "scripts": {
        "dev": "node esbuild.config.mjs",
        "build": "tsc -noEmit -skipLibCheck && node esbuild.config.mjs production",
        "version": "node version-bump.mjs && git add manifest.json versions.json"
    },
    "keywords": [],
    "author": "",
    "license": "MIT",
    "devDependencies": {
        "@types/node": "^16.11.6",
        "@typescript-eslint/eslint-plugin": "^5.29.0",
        "@typescript-eslint/parser": "^5.29.0",
        "builtin-modules": "^3.3.0",
        "esbuild": "0.17.3",
        "obsidian": "latest",
        "tslib": "2.4.0",
        "typescript": "4.7.4"
    }
}
```

## TypeScript Configuration (tsconfig.json)
```json
{
    "compilerOptions": {
        "baseUrl": ".",
        "inlineSourceMap": true,
        "inlineSources": true,
        "module": "ESNext",
        "target": "ES6",
        "allowJs": true,
        "noImplicitAny": true,
        "moduleResolution": "node",
        "importHelpers": true,
        "isolatedModules": true,
        "strictNullChecks": true,
        "lib": ["DOM", "ES5", "ES6", "ES7"]
    },
    "include": ["**/*.ts"]
}
```

## Build Configuration (esbuild.config.mjs)
```javascript
import esbuild from "esbuild";
import process from "process";
import builtins from "builtin-modules";

const banner =
`/*
THIS IS A GENERATED/BUNDLED FILE BY ESBUILD
if you want to view the source, please visit the github repository of this plugin
*/
`;

const prod = (process.argv[2] === 'production');

const context = await esbuild.context({
    banner: {
        js: banner,
    },
    entryPoints: ['main.ts'],
    bundle: true,
    external: [
        'obsidian',
        'electron',
        '@codemirror/autocomplete',
        '@codemirror/collab',
        '@codemirror/commands',
        '@codemirror/language',
        '@codemirror/lint',
        '@codemirror/search',
        '@codemirror/state',
        '@codemirror/view',
        '@lezer/common',
        '@lezer/highlight',
        '@lezer/lr',
        ...builtins],
    format: 'cjs',
    target: 'es2018',
    logLevel: "info",
    sourcemap: prod ? false : 'inline',
    treeShaking: true,
    outfile: 'main.js',
});

if (prod) {
    await context.rebuild();
    process.exit(0);
} else {
    await context.watch();
}
```

## Publishing Process

### 1. Prepare for Release
- Update `manifest.json` with new version number (e.g., "1.0.1")
- Update `minAppVersion` if needed
- Update `versions.json`: `{"1.0.1": "0.15.0"}`
- Build production version: `npm run build`

### 2. Create GitHub Release
- Create new GitHub release
- Tag version: Use exact version number without "v" prefix (e.g., "1.0.1")
- Upload files as binary attachments:
  - `manifest.json`
  - `main.js`
  - `styles.css` (if exists)
- Publish release

### 3. Submit to Community Plugins
- Ensure you have a `README.md` in repository root
- Check plugin guidelines: https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines
- Make pull request to: https://github.com/obsidianmd/obsidian-releases
- Edit `community-plugins.json` and add your plugin:
```json
{
    "id": "your-plugin-id",
    "name": "Your Plugin Name",
    "author": "Your Name",
    "description": "Plugin description",
    "repo": "username/repository-name"
}
```

### Version Bump Helper
```javascript
// version-bump.mjs
import { readFileSync, writeFileSync } from "fs";

const targetVersion = process.env.npm_package_version;

// Read minAppVersion from manifest.json
let manifest = JSON.parse(readFileSync("manifest.json", "utf8"));
const { minAppVersion } = manifest;
manifest.version = targetVersion;
writeFileSync("manifest.json", JSON.stringify(manifest, null, "\t"));

// Update versions.json
let versions = JSON.parse(readFileSync("versions.json", "utf8"));
versions[targetVersion] = minAppVersion;
writeFileSync("versions.json", JSON.stringify(versions, null, "\t"));
```

## Best Practices

### 1. Resource Cleanup
Always use registration methods for automatic cleanup:
- `this.registerEvent()` for Obsidian events
- `this.registerDomEvent()` for DOM events
- `this.registerInterval()` for intervals
- Component children are auto-unloaded

### 2. Error Handling
```typescript
try {
    await this.app.vault.modify(file, content);
} catch (error) {
    new Notice('Error: ' + error.message);
    console.error(error);
}
```

### 3. Async/Await
Use async/await for file operations and API calls:
```typescript
async onload() {
    await this.loadSettings();
    // Other initialization
}
```

### 4. Type Safety
Always import types from Obsidian:
```typescript
import { 
    Plugin, 
    TFile, 
    Editor, 
    MarkdownView,
    Notice 
} from 'obsidian';
```

### 5. Mobile Compatibility
- Avoid NodeJS-specific APIs unless `isDesktopOnly: true`
- Test on mobile if targeting mobile users
- Use responsive CSS

### 6. Performance
- Debounce frequent operations
- Cache expensive computations
- Use metadata cache instead of reading files repeatedly
- Avoid blocking the UI thread

## Common Patterns

### Debounced File Save
```typescript
import { debounce } from 'obsidian';

const debouncedSave = debounce(
    async (content: string) => {
        await this.saveSettings();
    },
    1000,
    true
);
```

### Notice with Timeout
```typescript
new Notice('Operation complete!', 5000); // 5 seconds
```

### Creating Menu Items
```typescript
import { Menu } from 'obsidian';

const menu = new Menu();

menu.addItem((item) =>
    item
        .setTitle('Menu item')
        .setIcon('dice')
        .onClick(() => {
            console.log('Clicked!');
        })
);

menu.showAtMouseEvent(evt);
```

### Suggest Modal
```typescript
import { FuzzySuggestModal, TFile } from 'obsidian';

class FileSuggestModal extends FuzzySuggestModal<TFile> {
    getItems(): TFile[] {
        return this.app.vault.getMarkdownFiles();
    }
    
    getItemText(file: TFile): string {
        return file.basename;
    }
    
    onChooseItem(file: TFile, evt: MouseEvent | KeyboardEvent) {
        new Notice(`Selected: ${file.basename}`);
    }
}

// Use it
new FileSuggestModal(this.app).open();
```

## API Reference

### Core Interfaces
- **App**: Main application object (`this.app`)
  - `vault`: File system operations
  - `workspace`: UI and layout
  - `metadataCache`: Cached file metadata
  - `fileManager`: High-level file operations
  
- **Vault**: File operations
  - `read(file)`: Read file content
  - `modify(file, data)`: Modify file
  - `create(path, data)`: Create file
  - `delete(file)`: Delete file
  - `rename(file, newPath)`: Rename file
  
- **Workspace**: UI operations
  - `getActiveFile()`: Get current file
  - `getActiveViewOfType()`: Get specific view type
  - `getLeavesOfType()`: Get all leaves of type
  - `createLeafBySplit()`: Split and create leaf

- **MetadataCache**: Metadata operations
  - `getFileCache(file)`: Get cached metadata
  - `on('changed', callback)`: Listen to metadata changes

## Debugging

### Console Logging
```typescript
console.log('Debug info:', data);
console.error('Error occurred:', error);
```

### Obsidian Developer Console
- Open with: Ctrl+Shift+I (Windows/Linux) or Cmd+Option+I (Mac)
- View plugin logs and errors
- Inspect DOM elements

### Hot Reload
Install "Hot Reload" plugin for development to auto-reload on changes.

## Common Issues and Solutions

### Issue: Plugin not loading
- Check manifest.json is valid JSON
- Ensure plugin is enabled in settings
- Check console for errors
- Verify minAppVersion compatibility

### Issue: TypeScript errors
- Run `npm install` to ensure dependencies are installed
- Check tsconfig.json configuration
- Verify Obsidian API types are up to date: `npm update`

### Issue: Changes not reflecting
- Ensure `npm run dev` is running
- Reload Obsidian (Ctrl+R)
- Check files are copied to correct plugin folder

## Additional Resources

- Official API Documentation: https://docs.obsidian.md
- API Type Definitions: https://github.com/obsidianmd/obsidian-api
- Sample Plugin: https://github.com/obsidianmd/obsidian-sample-plugin
- Plugin Developer Docs: https://marcus.se.net/obsidian-plugin-docs/
- Community Forum: https://forum.obsidian.md/c/developers-api/14
- Lucide Icons: https://lucide.dev/

## Claude's Implementation Approach

When building or editing an Obsidian plugin, Claude should:

1. **Start with structure**: Create or verify all required files (manifest.json, main.ts, package.json, etc.)
2. **Follow TypeScript conventions**: Use proper types from Obsidian API
3. **Use registration methods**: Always use `this.register*()` for cleanup
4. **Test incrementally**: Make small changes and verify they work
5. **Handle errors gracefully**: Use try-catch and show user-friendly notices
6. **Comment complex logic**: Explain non-obvious code
7. **Follow Obsidian patterns**: Use established patterns from documentation
8. **Consider mobile**: Avoid desktop-only APIs unless necessary
9. **Optimize performance**: Be mindful of file operations and caching
10. **Document features**: Add clear comments and README documentation

## Example: Complete Plugin

Here's a complete working example of a simple plugin:

```typescript
// main.ts
import { Plugin, Notice, MarkdownView } from 'obsidian';

interface WordCountSettings {
    showInStatusBar: boolean;
}

const DEFAULT_SETTINGS: WordCountSettings = {
    showInStatusBar: true
}

export default class WordCountPlugin extends Plugin {
    settings: WordCountSettings;
    statusBarItem: HTMLElement;

    async onload() {
        await this.loadSettings();

        // Add status bar item
        this.statusBarItem = this.addStatusBarItem();
        this.updateStatusBar();

        // Register event to update on file change
        this.registerEvent(
            this.app.workspace.on('active-leaf-change', () => {
                this.updateStatusBar();
            })
        );

        // Add command
        this.addCommand({
            id: 'show-word-count',
            name: 'Show Word Count',
            callback: () => {
                const count = this.getWordCount();
                new Notice(`Word count: ${count}`);
            }
        });
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    getWordCount(): number {
        const view = this.app.workspace.getActiveViewOfType(MarkdownView);
        if (!view) return 0;
        
        const content = view.editor.getValue();
        const words = content.split(/\s+/).filter(word => word.length > 0);
        return words.length;
    }

    updateStatusBar() {
        if (!this.settings.showInStatusBar) {
            this.statusBarItem.setText('');
            return;
        }

        const count = this.getWordCount();
        this.statusBarItem.setText(`Words: ${count}`);
    }

    onunload() {
        // Cleanup happens automatically for registered events
    }
}
```

```json
// manifest.json
{
    "id": "word-count",
    "name": "Word Count",
    "version": "1.0.0",
    "minAppVersion": "0.15.0",
    "description": "Shows word count in status bar",
    "author": "Your Name",
    "isDesktopOnly": false
}
```

This skill provides comprehensive guidance for building Obsidian plugins using TypeScript and the Obsidian API.
