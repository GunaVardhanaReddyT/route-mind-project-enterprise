-- Seed Mumbai (hub_id=2) and Bangalore (hub_id=3)
-- Run: docker-compose exec -T db psql -U routemind -d routemind_db < seed_mumbai_bangalore.sql

-- MUMBAI (hub_id=2)
-- Depot: 19.0760, 72.8777 (Mumbai Central)

-- Mumbai Vehicles
INSERT INTO vehicles (id, plate_number, capacity_kg, hub_id, is_active) VALUES
(11, 'MH-02-AB-1234', 500, 2, true),
(12, 'MH-02-CD-5678', 500, 2, true),
(13, 'MH-02-EF-9012', 500, 2, true)
ON CONFLICT (id) DO NOTHING;

-- Mumbai Stops (10 stops across Mumbai)
INSERT INTO stops (id, address, lat, lon, time_window_start, time_window_end, priority, package_count, total_weight_kg, zone, hub_id, is_completed) VALUES
(101, 'Andheri East, Mumbai', 19.1136, 72.8697, '09:00', '13:00', 'high', 5, 25.0, 'west', 2, false),
(102, 'Bandra West, Mumbai', 19.0596, 72.8295, '10:00', '14:00', 'medium', 3, 15.0, 'west', 2, false),
(103, 'Powai, Mumbai', 19.1176, 72.9060, '09:00', '12:00', 'high', 4, 20.0, 'east', 2, false),
(104, 'Worli, Mumbai', 19.0133, 72.8148, '11:00', '15:00', 'low', 2, 10.0, 'south', 2, false),
(105, 'Thane West, Mumbai', 19.2183, 72.9781, '09:30', '13:30', 'medium', 4, 18.0, 'east', 2, false),
(106, 'Dadar East, Mumbai', 19.0178, 72.8478, '10:00', '14:00', 'medium', 3, 14.0, 'central', 2, false),
(107, 'Colaba, Mumbai', 18.9067, 72.8147, '11:00', '15:00', 'low', 2, 12.0, 'south', 2, false),
(108, 'Juhu, Mumbai', 19.0990, 72.8267, '09:00', '13:00', 'high', 5, 22.0, 'west', 2, false),
(109, 'Malad West, Mumbai', 19.1866, 72.8486, '10:00', '14:00', 'medium', 3, 16.0, 'north', 2, false),
(110, 'Goregaon East, Mumbai', 19.1653, 72.8526, '09:30', '13:30', 'medium', 4, 19.0, 'north', 2, false)
ON CONFLICT (id) DO NOTHING;

-- BANGALORE (hub_id=3)
-- Depot: 12.9716, 77.5946 (Bangalore Central)

-- Bangalore Vehicles
INSERT INTO vehicles (id, plate_number, capacity_kg, hub_id, is_active) VALUES
(21, 'KA-01-MN-3456', 500, 3, true),
(22, 'KA-01-OP-7890', 500, 3, true),
(23, 'KA-01-QR-1122', 500, 3, true)
ON CONFLICT (id) DO NOTHING;

-- Bangalore Stops (10 stops across Bangalore)
INSERT INTO stops (id, address, lat, lon, time_window_start, time_window_end, priority, package_count, total_weight_kg, zone, hub_id, is_completed) VALUES
(201, 'Koramangala, Bangalore', 12.9352, 77.6245, '09:00', '13:00', 'high', 5, 24.0, 'south', 3, false),
(202, 'Whitefield, Bangalore', 12.9698, 77.7499, '10:00', '14:00', 'medium', 3, 16.0, 'east', 3, false),
(203, 'Indiranagar, Bangalore', 12.9716, 77.6412, '09:00', '12:00', 'high', 4, 21.0, 'central', 3, false),
(204, 'HSR Layout, Bangalore', 12.9121, 77.6446, '11:00', '15:00', 'low', 2, 11.0, 'south', 3, false),
(205, 'Jayanagar, Bangalore', 12.9250, 77.5838, '09:30', '13:30', 'medium', 4, 19.0, 'south', 3, false),
(206, 'Malleshwaram, Bangalore', 13.0042, 77.5693, '10:00', '14:00', 'medium', 3, 15.0, 'north', 3, false),
(207, 'Electronic City, Bangalore', 12.8456, 77.6603, '11:00', '15:00', 'low', 2, 13.0, 'south', 3, false),
(208, 'Marathahalli, Bangalore', 12.9591, 77.7012, '09:00', '13:00', 'high', 5, 23.0, 'east', 3, false),
(209, 'Yelahanka, Bangalore', 13.1007, 77.5963, '10:00', '14:00', 'medium', 3, 17.0, 'north', 3, false),
(210, 'BTM Layout, Bangalore', 12.9165, 77.6101, '09:30', '13:30', 'medium', 4, 20.0, 'south', 3, false)
ON CONFLICT (id) DO NOTHING;

-- Verify counts
SELECT 'Mumbai Vehicles' as table_name, COUNT(*) as count FROM vehicles WHERE hub_id = 2
UNION ALL
SELECT 'Mumbai Stops', COUNT(*) FROM stops WHERE hub_id = 2
UNION ALL
SELECT 'Bangalore Vehicles', COUNT(*) FROM vehicles WHERE hub_id = 3
UNION ALL
SELECT 'Bangalore Stops', COUNT(*) FROM stops WHERE hub_id = 3;
