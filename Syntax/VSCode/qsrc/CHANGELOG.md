# Change Log
All notable changes to the "qsrc" extension will be documented in this file.

## 0.2.0
- Initial release
- Ported atom grammars to VS Code

## 0.2.1
- Added missing file
- Updated extension to work with newer VS Code.

### 0.2.2
- Added whitespace matching for !{ and :

### 0.2.3
- Added more keywords from QGen.

### 0.2.4
- Fix for "" strings.

### 0.2.5
- Added indentation rules

### 0.2.6
- Fixes for indent rules

### 0.2.7
- Fix for system variables not highlighting '$' also.

### 0.2.8
- Fix line comments that start with '&!'
- Reformatted the syntax file to fit with VSCode better.
- Fixed the '*' not highlighting with clear, clr, cls, nl, pl and p variables.
- Fixed 'p' variables not highlighting at all.
- Fixed indentation rules to not apply for single line if statements.

### 0.2.9
- Added '/' '!' '*' to support functions.
- Added multiline comments regex from slanon. So "!'" "!{" "}" comments now work.

