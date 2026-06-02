Follow these commands to create a worktree

1. Get the current project's folder name.
2. Create a folder adjacent to the current project's folder and name it {current project folder name}_worktrees. For example, if the current prohect folder is named myapp, create a folder called myapp_worktrees. Both myapp and myapp_worktrees should have the same parent folder.

3. Create a git worktree and branch named $ARGUMENTS from the main project folder and save it inside the {current project folder name}_worktrees folder that was created.

4. cd into the new $ARGUMENTS worktree folder.