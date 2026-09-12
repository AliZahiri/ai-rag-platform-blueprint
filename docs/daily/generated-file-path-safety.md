# Generated file path safety

<!-- daily-pr-task: generated-file-path-safety -->

Daily automation rejects noncanonical paths, traversal, control characters,
backslashes, Git metadata paths, duplicate destinations, and symlink components.
Completion checks use the same destination validation as writes, so they cannot
read completion markers through an external symlink.

Every destination is checked before any directory is created or file is written.
A rejected later destination therefore leaves earlier files untouched. Existing
regular files can still evolve, and the repository root itself may be a symlink.

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.
The regression suite covers internal, external, and dangling symlinks, metadata
paths, duplicate files, directory targets, and partial-write prevention.

This is a trusted-checkout control, not a filesystem sandbox. It does not prevent
a concurrent process from replacing a validated component after preflight, and
write errors such as a full disk can still leave a partially applied task.
Run the generator only in a checkout that other processes are not mutating.
Roll back the implementation commit if normal task generation regresses.
