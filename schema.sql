-- Smart Travel Planner Database Schema (MySQL)
-- Company Base: Ahmedabad, Gujarat, India
-- Currency: Indian Rupee (₹)

CREATE DATABASE IF NOT EXISTS smart_travel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_travel_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    city VARCHAR(100) DEFAULT 'Ahmedabad',
    state VARCHAR(100) DEFAULT 'Gujarat',
    dietary_preference ENUM('No Preference', 'Pure Vegetarian', 'Jain Food', 'Vegan', 'Non-Vegetarian') DEFAULT 'Pure Vegetarian',
    role ENUM('user', 'admin') DEFAULT 'user',
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Destinations Table
CREATE TABLE IF NOT EXISTS destinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    state VARCHAR(100) NOT NULL,
    category ENUM('Heritage', 'Hill Station', 'Beach', 'Spiritual', 'Wildlife', 'Desert', 'Adventure') NOT NULL,
    tagline VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    avg_cost_per_day INT NOT NULL COMMENT 'Average daily cost per person in INR',
    best_time_to_visit VARCHAR(100) NOT NULL,
    ahmedabad_connectivity VARCHAR(255) DEFAULT 'Direct Flight / Overnight Express Train from Ahmedabad',
    featured TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Trips Table
CREATE TABLE IF NOT EXISTS trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    destination_id INT NOT NULL,
    trip_title VARCHAR(200) NOT NULL,
    origin_city VARCHAR(100) DEFAULT 'Ahmedabad, Gujarat',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INT NOT NULL,
    travelers_count INT NOT NULL DEFAULT 1,
    travel_style ENUM('Backpacker', 'Comfort', 'Luxury') DEFAULT 'Comfort',
    total_budget INT NOT NULL COMMENT 'Total allocated budget in INR',
    estimated_cost INT NOT NULL COMMENT 'Estimated itinerary cost in INR',
    status ENUM('Planning', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Planning',
    notes TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Itineraries Table
CREATE TABLE IF NOT EXISTS itineraries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    day_number INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    morning_activity TEXT NOT NULL,
    afternoon_activity TEXT NOT NULL,
    evening_activity TEXT NOT NULL,
    meal_recommendation VARCHAR(255) NOT NULL,
    estimated_spend INT NOT NULL COMMENT 'Daily spend in INR',
    transport_tips VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- SEED DATA

-- Initial Users (Passwords: pbkdf2:sha256 or bcrypt hash, for seed: admin123 and user123)
-- admin: 'admin@smarttravel.in' / 'admin123'
-- user: 'rahul.patel@gmail.com' / 'user123'
INSERT INTO users (id, name, email, password_hash, phone, city, state, dietary_preference, role, status) VALUES
(1, 'System Administrator', 'admin@smarttravel.in', 'scrypt:32768:8:1$kX1w$admin123hashed', '+91 98250 11223', 'Ahmedabad', 'Gujarat', 'Pure Vegetarian', 'admin', 'active'),
(2, 'Rahul Patel', 'rahul.patel@gmail.com', 'scrypt:32768:8:1$uY2z$user123hashed', '+91 99090 44556', 'Ahmedabad', 'Gujarat', 'Pure Vegetarian', 'user', 'active'),
(3, 'Ananya Sharma', 'ananya.sharma@outlook.com', 'scrypt:32768:8:1$pA3b$user123hashed', '+91 98110 55667', 'Vadodara', 'Gujarat', 'Jain Food', 'user', 'active')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Initial Indian Destinations
INSERT INTO destinations (id, name, state, category, tagline, description, image_url, avg_cost_per_day, best_time_to_visit, ahmedabad_connectivity, featured) VALUES
(1, 'Jaipur', 'Rajasthan', 'Heritage', 'The Pink City of Royal Palaces and Amber Forts', 'Immerse yourself in Rajasthani royalty, majestic hilltop fortresses, vibrant bazaars, and opulent royal havelis.', 'https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1000&q=80', 3200, 'October to March', 'Overnight Vande Bharat / Express Train (9 hrs) or 1h 10m direct flight from AMD', 1),
(2, 'Udaipur', 'Rajasthan', 'Heritage', 'The City of Lakes and Royal Venetian Elegance', 'Romantic boat rides across Lake Pichola, towering white marble palaces, and scenic rooftop dining overlooking the Aravalli hills.', 'https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?auto=format&fit=crop&w=1000&q=80', 3800, 'September to March', 'Scenic 4.5 hrs highway drive (NH48) or daily express train from Ahmedabad', 1),
(3, 'Rann of Kutch', 'Gujarat', 'Desert', 'The Enchanting White Salt Desert & Cultural Oasis', 'Witness boundless shimmering white salt flats under moonlight, Kutchi handicrafts, tent cities, and traditional folk dances.', 'https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=1000&q=80', 4500, 'November to February (Rann Utsav)', 'Direct Bhuj AC express train or 6.5 hrs smooth road drive from Ahmedabad', 1),
(4, 'Munnar', 'Kerala', 'Hill Station', 'Emerald Tea Terraces & Mist-Clad Western Ghats', 'Sprawling carpet-like tea plantations, cool misty mountain breezes, spice gardens, and cascading waterfalls.', 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1000&q=80', 3400, 'September to April', 'Direct flight AMD to Cochin (COK, 2h 15m), followed by 3 hrs scenic ghat drive', 1),
(5, 'Goa', 'Goa', 'Beach', 'Sun-Kissed Beaches, Portuguese Quarters & Seafood', 'From peaceful golden southern sands and UNESCO Latin quarters to vibrant beach shacks and sunset cruises.', 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1000&q=80', 4200, 'November to March', 'Direct non-stop flight from Ahmedabad to Mopa/Dabolim (1h 35m)', 1),
(6, 'Leh-Ladakh', 'Ladakh', 'Adventure', 'The Rooftop of the World with Azure Glacial Lakes', 'Dramatic high-altitude barren passes, Buddhist gompas, Pangong Tso crystal lake, and Nubra Valley sand dunes.', 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=1000&q=80', 5800, 'May to September', 'Connecting morning flight via Delhi to Leh (IXL) from Ahmedabad', 1),
(7, 'Varanasi', 'Uttar Pradesh', 'Spiritual', 'The Ancient City of Ghats, Chants & Ganga Aarti', 'Soul-stirring evening Ganga Aarti at Dashashwamedh Ghat, sunrise boat rides, narrow heritage alleys, and banarasi sweets.', 'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1000&q=80', 2500, 'October to March', 'Direct flight AMD to Varanasi (VNS, 2 hrs) or Sabarmati-Varanasi Express train', 1),
(8, 'Manali', 'Himachal Pradesh', 'Hill Station', 'Pine Valleys, Snow Adventures & Rohtang Pass', 'Alpine meadows, paragliding in Solang Valley, hot water sulfur springs of Vashisht, and Himalayan mountain cafes.', 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1000&q=80', 3600, 'October to June', 'Direct flight AMD to Chandigarh (CHG, 1h 45m) then scenic highway drive', 1),
(9, 'Rishikesh', 'Uttarakhand', 'Adventure', 'Yoga Capital of the World & Holy Ganga Rapids', 'White-water river rafting, peaceful evening aarti at Triveni Ghat, suspension bridges, and cliffside yoga retreats.', 'https://images.unsplash.com/photo-1600100397608-f010f444f434?auto=format&fit=crop&w=1000&q=80', 2900, 'September to May', 'Flight AMD to Dehradun (Jolly Grant Airport, 1h 50m direct)', 0),
(10, 'Darjeeling', 'West Bengal', 'Hill Station', 'Toy Train Heritage & Views of Mount Kanchenjunga', 'World-famous vintage steam railway, colonial tea estates, Tiger Hill sunrise over Himalayan snow peaks.', 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1000&q=80', 3700, 'March to May & October to December', 'Flight AMD to Bagdogra (IXB) with short layover or direct seasonal flight', 0),
(11, 'Hampi', 'Karnataka', 'Heritage', 'UNESCO Ruins of the Great Vijayanagara Empire', 'Gigantic boulder-strewn landscapes, magnificent temple architecture, stone chariot, and Coracle boat rides on the Tungabhadra.', 'https://images.unsplash.com/photo-1600100397608-f010f444f434?auto=format&fit=crop&w=1000&q=80', 2700, 'October to March', 'Connecting train or flight AMD to Hubballi (HBX) / Bengaluru', 0),
(12, 'Srinagar', 'Jammu & Kashmir', 'Hill Station', 'Paradise on Earth: Dal Lake Shikaras & Mughal Gardens', 'Charming wooden houseboats, floating vegetable markets, Nishat and Shalimar gardens, and snow-draped Pir Panjal vistas.', 'https://images.unsplash.com/photo-1566837945700-30057527ade0?auto=format&fit=crop&w=1000&q=80', 4800, 'April to October & Dec-Feb for Snow', 'Direct connecting flight from Ahmedabad to Srinagar (SXR)', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Sample Trips
INSERT INTO trips (id, user_id, destination_id, trip_title, origin_city, start_date, end_date, total_days, travelers_count, travel_style, total_budget, estimated_cost, status, notes) VALUES
(1, 2, 2, 'Royal Romance & Palaces of Udaipur', 'Ahmedabad, Gujarat', '2026-11-15', '2026-11-18', 4, 2, 'Comfort', 35000, 30400, 'Confirmed', 'Departing early morning by car from SG Highway, Ahmedabad via NH48. Pure Veg dining planned.'),
(2, 2, 3, 'Kutch Rann Utsav Moonlight Exploration', 'Ahmedabad, Gujarat', '2026-12-20', '2026-12-23', 4, 2, 'Comfort', 40000, 36000, 'Planning', 'Full moon night tent stay at Dhordo, Kutch. Handicraft shopping at Bhujodi.')
ON DUPLICATE KEY UPDATE trip_title=VALUES(trip_title);

-- Sample Itinerary for Trip 1 (Udaipur from Ahmedabad)
INSERT INTO itineraries (trip_id, day_number, title, morning_activity, afternoon_activity, evening_activity, meal_recommendation, estimated_spend, transport_tips) VALUES
(1, 1, 'Arrival & Sunset on Lake Pichola', 'Drive from Ahmedabad via Himatnagar/Shamlaji (4.5 hrs). Check into heritage haveli hotel.', 'Visit Bagore Ki Haveli museum and explore the local clock tower marketplace.', 'Sunset boat cruise on Lake Pichola with view of Jag Mandir and Lake Palace.', 'Traditional Rajasthani Dal Baati Churma at Natraj Dining Hall', 6800, 'Private Car / Cab from Ahmedabad'),
(1, 2, 'City Palace & Vintage Cars', 'Guided tour of the sprawling City Palace complex and crystal gallery.', 'Traditional lunch and stroll through Saheliyon Ki Bari royal gardens.', 'Dharohar folk dance show with puppet artists at Bagore Ki Haveli.', 'Lakeside rooftop dining with illuminated palace view at Ambrai', 8500, 'Auto-rickshaw or walking around Old City'),
(1, 3, 'Monsoon Palace & Sajjangarh Wildlife', 'Scenic uphill drive to Sajjangarh Monsoon Palace for panoramic Aravalli vistas.', 'Craft tour of Shilpgram rural arts & crafts complex.', 'Peaceful boat ride at Fateh Sagar Lake and evening snacks at Sukhadia Circle.', 'Kathiyawadi & Mewari fusion thali at Gordhan Thal', 7200, 'Local cab rental for full day'),
(1, 4, 'Kumbhalgarh Fort Excursion & Return to Ahmedabad', 'Morning check-out and drive to Kumbhalgarh Fort (Great Wall of India).', 'Explore the massive ramparts and Jain temples of Kumbhalgarh.', 'Evening scenic highway drive back to Ahmedabad via NH48.', 'Midway dinner at Honest / Highway King Restaurant', 7900, 'Highway return drive to Ahmedabad')
ON DUPLICATE KEY UPDATE title=VALUES(title);
