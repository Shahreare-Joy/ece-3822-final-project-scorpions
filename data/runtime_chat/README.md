# Runtime Chat Buffers

This folder is for temporary local/session chat bridge files created while the
arcade or a launched game is running.

These files are not the synthetic dataset and should not be used as seed data.
The cleanup logic removes a session buffer when the launched game exits or when
the arcade explicitly closes that session.
