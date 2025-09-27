-- 1. Create schema
DROP SCHEMA IF EXISTS holidays CASCADE;
CREATE SCHEMA IF NOT EXISTS holidays;

-- 2. Create the table within the schema
DROP TABLE IF EXISTS holidays.holiday_requests CASCADE;
CREATE TABLE IF NOT EXISTS holidays.holiday_requests (
  request_id SERIAL PRIMARY KEY,
  employee_name VARCHAR(255) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL,
  manager_note TEXT
);

-- 3. Insert sample holiday requests for all team members
INSERT INTO holidays.holiday_requests (employee_name, start_date, end_date, status, manager_note)
  VALUES
    ('Alex Thompson', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Sarah Johnson', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Michael Chen', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Emily Rodriguez', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('David Wilson', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Jessica Brown', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Ryan Martinez', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Jules Damji', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Amanda Davis', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Kevin Liu', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Maria Garcia', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('James Taylor', '2025-12-01', '2025-12-12', 'Pending', ''),
    ('Lisa Anderson', '2025-12-01', '2025-12-12', 'Pending', '');


-- 4. The Lakebase resource in the App already allows connecting to Lakebase database instance and the database.
--    Grant permissions on the required schema and table.
--    Replace the <CLIENT_ID> with the value from your App
-- simple_app client id ("6706ac70-6ca1-4104-b72d-028a0eaa716f)
-- holiday_request_app client id("277f0bb4-7c1f-4f91-81fd-ec1f83a9fdb9")
GRANT USAGE ON SCHEMA holidays TO "079c7c94-42cb-4eaf-9048-a01c5652fd5f";
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE holidays.holiday_requests TO "079c7c94-42cb-4eaf-9048-a01c5652fd5f";

SELECT * FROM holidays.holiday_requests;