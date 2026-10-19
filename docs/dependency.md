Routes call services only. Never repositories or SQL.
Services call repository interfaces only. Never sqlite3, and never Flask objects like request.
The domain package imports nothing from other layers.
Only app/__init__.py (the composition root) knows which concrete class is used.
Modules talk to each other through services, never by reaching into another module’s tables.