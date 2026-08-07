-- Create hubs table for dynamic hub management
CREATE TABLE IF NOT EXISTS hubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    depot_lat FLOAT NOT NULL,
    depot_lon FLOAT NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Seed initial hubs
INSERT INTO hubs (id, name, city, depot_lat, depot_lon, address) VALUES
(1, 'Delhi NCR Hub', 'Delhi', 28.6139, 77.2090, 'Connaught Place, New Delhi'),
(2, 'Mumbai Hub', 'Mumbai', 19.0760, 72.8777, 'CST, Mumbai'),
(3, 'Bangalore Hub', 'Bangalore', 12.9716, 77.5946, 'MG Road, Bangalore')
ON CONFLICT (id) DO NOTHING;

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_hubs_city ON hubs(city);
CREATE INDEX IF NOT EXISTS idx_hubs_active ON hubs(is_active);
