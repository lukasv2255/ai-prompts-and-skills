# FastAPI Ingest API

Tento skill je sablona pro FastAPI server, ktery prijima data z externiho collectoru a uklada je do SQLite nebo PostgreSQL podle prostredi. Hodi se pro projekty, kde lokalni skript neco sbira a potrebuje to bezpecne posilat do webove aplikace nebo na Railway.

Dava zakladni kostru: endpointy, auth pres API key, validaci vstupu, bulk ingest a health check. Je to dobry start, kdyz nechces pokazde znovu vymyslet stejny backendovy vzor.
