# Command selection

Choose commands in this order:

1. Explicit commands in the nearest `AGENTS.md`.
2. Contributor documentation and repository README.
3. CI workflow commands for the affected package.
4. Package/task-runner scripts.
5. Language-native defaults only when the repository has no declared command.

For monorepos, scope checks to the affected package first. Run root aggregation
only when shared interfaces, lockfiles, build configuration, or release output
changed.

Generated files and lockfiles should be validated by their canonical generator,
not hand-edited or text-merged when regeneration is available.
