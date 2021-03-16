# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
 * Put the `script` property always as first on a node otherwise Godot will not properly load a node.
 * Do not crash when serializing node-like values.
 * Tweak serialization output to be as close as possible to what Godot would output, to get cleaner diffs in version control.