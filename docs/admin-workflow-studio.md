# Admin Workflow Studio

The workflow studio adds an admin-facing draft registry to the platform. This
first implementation slice focuses on draft authoring foundations:

- durable workflow lineage, draft-head, and immutable revision storage
- JSON APIs for registry list, create, fetch, save, and editor metadata
- embedded HTML pages for registry browsing and draft editing
- centralized field-help metadata for modal-driven guidance in the editor

Future phases will layer validation, publish compilation, immutable version
details, and sharing grants onto the same surfaces.
