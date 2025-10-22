CREATE DATABASE organization_catalog;

CREATE USER catalog_user WITH PASSWORD 'catalog_password';

GRANT ALL PRIVILEGES ON DATABASE organization_catalog TO catalog_user;

\c organization_catalog;

GRANT ALL ON SCHEMA public TO catalog_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO catalog_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO catalog_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO catalog_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO catalog_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO catalog_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO catalog_user;