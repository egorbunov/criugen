#pragma once

/**
 * moves fd from old to new one
 * new_fd must be free fd, so there is no
 * any files opened at it
 * @returns 0 if ok, else -1 is returned
 */
int move_fd(int old_fd, int new_fd);

