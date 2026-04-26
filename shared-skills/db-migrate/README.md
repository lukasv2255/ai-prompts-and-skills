# DB Migrate

Tento skill resi prenos dat mezi databazemi a datovymi zdroji, typicky SQLite, PostgreSQL, CSV nebo HTTP ingest endpointy. Pouziva se pri migraci na Railway, obnove ztratene DB, slouceni historickych dat nebo pri presunu mezi stroji.

Dulezity je na nem konzervativni postup: zachovani timestampu, davkove zpracovani, deduplikace a moznost kontrolovat prubeh. Neni to jen "kopie tabulky", ale bezpecny migracni workflow.
