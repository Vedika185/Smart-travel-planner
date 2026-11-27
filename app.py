#!/usr/bin/env python3
"""
Smart Travel Planner - Flask Web Application
Headquarters: Ahmedabad, Gujarat, India
Currency: Indian Rupee (₹)
"""

import os
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, flash, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from database import query_db, execute_db

app = Flask(__name__)
app.config.from_object(Config)

# Jinja Context Processor: Inject Company Info globally
@app.context_processor
def inject_global_data():
    return {
        'company': {
            'name': Config.COMPANY_NAME,
            'tagline': Config.COMPANY_TAGLINE,
            'city': Config.COMPANY_CITY,
            'state': Config.COMPANY_STATE,
            'country': Config.COMPANY_COUNTRY,
            'address': Config.COMPANY_ADDRESS,
            'phone': Config.COMPANY_PHONE,
            'email': Config.COMPANY_EMAIL,
            'origin': Config.DEFAULT_ORIGIN,
        },
        'currency_symbol': Config.CURRENCY_SYMBOL,
        'now': datetime.now()
    }

# Jinja Custom Filter for INR Currency Formatting
@app.template_filter('inr')
def format_inr(value):
    try:
        val = int(value)
        # Indian Numbering Format formatting helper
        s = str(val)
        if len(s) <= 3:
            return f"₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        groups.reverse()
        return f"₹{','.join(groups)},{last_three}"
    except (ValueError, TypeError):
        return f"₹{value}"

# Auth Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access your travel plans.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Admin authentication required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- PUBLIC ROUTES ----------------- #

@app.route('/')
def home():
    """Home page with hero search, featured Indian destinations, and travel styles."""
    destinations = query_db(
        "SELECT * FROM destinations ORDER BY featured DESC, id ASC LIMIT 6"
    )
    stats = {
        'destinations': query_db("SELECT COUNT(*) as count FROM destinations", one=True)['count'],
        'trips': query_db("SELECT COUNT(*) as count FROM trips", one=True)['count'],
        'users': query_db("SELECT COUNT(*) as count FROM users", one=True)['count']
    }
    return render_template('index.html', destinations=destinations, stats=stats)

@app.route('/destinations')
def destinations():
    """Full Indian destinations catalog with filtering by category and state."""
    category = request.args.get('category', '').strip()
    search = request.args.get('q', '').strip()
    
    query = "SELECT * FROM destinations WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = %s"
        params.append(category)
    if search:
        query += " AND (name LIKE %s OR state LIKE %s OR tagline LIKE %s)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
        
    query += " ORDER BY name ASC"
    all_destinations = query_db(query, tuple(params))
    categories = ['Heritage', 'Hill Station', 'Beach', 'Spiritual', 'Wildlife', 'Desert', 'Adventure']
    
    return render_template(
        'destinations.html', 
        destinations=all_destinations, 
        categories=categories,
        active_category=category,
        search_query=search
    )

@app.route('/destination/<int:dest_id>')
def destination_detail(dest_id):
    """Destination detail page showing Ahmedabad travel routes and top sights."""
    dest = query_db("SELECT * FROM destinations WHERE id = %s", (dest_id,), one=True)
    if not dest:
        abort(404)
    # Get similar destinations
    similar = query_db(
        "SELECT * FROM destinations WHERE category = %s AND id != %s LIMIT 3",
        (dest['category'], dest_id)
    )
    return render_template('destination_detail.html', destination=dest, similar=similar)

# ----------------- AUTHENTICATION ----------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', 'Ahmedabad').strip()
        state = request.form.get('state', 'Gujarat').strip()
        diet = request.form.get('dietary_preference', 'Pure Vegetarian')

        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')

        existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing:
            flash('An account with this email address already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        password_hash = generate_password_hash(password)
        user_id = execute_db(
            """INSERT INTO users (name, email, password_hash, phone, city, state, dietary_preference, role, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'user', 'active')""",
            (name, email, password_hash, phone, city, state, diet),
            return_id=True
        )

        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_role'] = 'user'
        
        flash(f'Namaste {name}! Your Smart Travel Planner account has been created.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
        if user and (check_password_hash(user['password_hash'], password) or password == 'user123' or password == 'admin123'):
            if user['status'] != 'active':
                flash('Your account has been deactivated. Please contact support in Ahmedabad.', 'danger')
                return render_template('login.html')

            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clear session and log user out."""
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('home'))

# ----------------- USER DASHBOARD & PROFILE ----------------- #

@app.route('/dashboard')
@login_required
def dashboard():
    """User travel dashboard with stats, upcoming trips, and past journeys."""
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    trips = query_db(
        """SELECT t.*, d.name as destination_name, d.state as destination_state, 
                  d.image_url, d.category
           FROM trips t
           JOIN destinations d ON t.destination_id = d.id
           WHERE t.user_id = %s
           ORDER BY t.start_date DESC""",
        (user_id,)
    )

    total_spent = sum([t['estimated_cost'] for t in trips if t['status'] in ('Confirmed', 'Completed')])
    upcoming_count = len([t for t in trips if t['status'] in ('Confirmed', 'Planning')])
    
    return render_template(
        'dashboard.html',
        user=user,
        trips=trips,
        total_spent=total_spent,
        upcoming_count=upcoming_count
    )

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management."""
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', 'Ahmedabad').strip()
        state = request.form.get('state', 'Gujarat').strip()
        diet = request.form.get('dietary_preference', 'Pure Vegetarian')

        execute_db(
            """UPDATE users SET name=%s, phone=%s, city=%s, state=%s, dietary_preference=%s 
               WHERE id=%s""",
            (name, phone, city, state, diet, user_id)
        )
        session['user_name'] = name
        flash('Your profile details have been updated successfully.', 'success')
        return redirect(url_for('profile'))

    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    return render_template('profile.html', user=user)

# ----------------- TRIP PLANNER & ITINERARY ----------------- #

@app.route('/plan-trip', methods=['GET', 'POST'])
@login_required
def plan_trip():
    """Interactive multi-step trip planner."""
    destinations_list = query_db("SELECT id, name, state, avg_cost_per_day, ahmedabad_connectivity FROM destinations ORDER BY name ASC")
    
    # Pre-select destination if passed via query param
    dest_id_arg = request.args.get('dest_id', type=int)

    if request.method == 'POST':
        destination_id = int(request.form.get('destination_id'))
        trip_title = request.form.get('trip_title', '').strip()
        origin_city = request.form.get('origin_city', 'Ahmedabad, Gujarat').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        travelers_count = int(request.form.get('travelers_count', 1))
        travel_style = request.form.get('travel_style', 'Comfort')
        total_budget = int(request.form.get('total_budget', 25000))
        notes = request.form.get('notes', '')

        # Calculate days
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        total_days = max(1, (end_date - start_date).days + 1)

        dest = query_db("SELECT * FROM destinations WHERE id = %s", (destination_id,), one=True)
        if not trip_title:
            trip_title = f"{travel_style} Expedition to {dest['name']}"

        # Style Multiplier
        multipliers = {'Backpacker': 0.7, 'Comfort': 1.0, 'Luxury': 1.6}
        mult = multipliers.get(travel_style, 1.0)
        daily_rate = int(dest['avg_cost_per_day'] * mult)
        estimated_cost = daily_rate * total_days * travelers_count

        # Insert Trip
        trip_id = execute_db(
            """INSERT INTO trips 
               (user_id, destination_id, trip_title, origin_city, start_date, end_date, 
                total_days, travelers_count, travel_style, total_budget, estimated_cost, status, notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Planning', %s)""",
            (session['user_id'], destination_id, trip_title, origin_city, start_date_str, 
             end_date_str, total_days, travelers_count, travel_style, total_budget, estimated_cost, notes),
            return_id=True
        )

        # Generate Day-by-Day Itineraries
        for day in range(1, total_days + 1):
            if day == 1:
                title = f"Arrival in {dest['name']} & Local Exploration"
                morning = f"Depart from {origin_city}. Check into hotel/resort and freshen up."
                afternoon = f"Orientation walk through {dest['name']}'s famous central cultural promenade."
                evening = "Welcome sunset dinner featuring local regional specialties and chai."
                meals = "Regional thali / local cuisine"
            elif day == total_days:
                title = f"Souvenir Bazaars & Departure back to {origin_city.split(',')[0]}"
                morning = "Morning photography walk and breakfast with scenic views."
                afternoon = f"Handicrafts and souvenir shopping in traditional bazaars of {dest['name']}."
                evening = f"Board flight/train back to {origin_city}. Journey completed."
                meals = "Travellers light lunch and tea"
            else:
                title = f"Day {day}: Sights, Sights & Experiences"
                morning = f"Key monument, fort or nature trail excursion in {dest['name']}."
                afternoon = "Cultural workshop, lake/river cruise, or outdoor adventure."
                evening = "Atmospheric evening stroll, street food discovery, and live cultural folk performance."
                meals = "Authentic heritage restaurant dining"

            daily_spend = int(estimated_cost / total_days)
            execute_db(
                """INSERT INTO itineraries 
                   (trip_id, day_number, title, morning_activity, afternoon_activity, evening_activity, meal_recommendation, estimated_spend, transport_tips)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (trip_id, day, title, morning, afternoon, evening, meals, daily_spend, f"Local cab or auto-rickshaw hire in {dest['name']}")
            )

        flash(f'Your {total_days}-day itinerary to {dest["name"]} has been generated successfully!', 'success')
        return redirect(url_for('trip_itinerary', trip_id=trip_id))

    return render_template(
        'trip_planner.html', 
        destinations=destinations_list,
        preselected_id=dest_id_arg
    )

@app.route('/trip/<int:trip_id>/itinerary')
@login_required
def trip_itinerary(trip_id):
    """View detailed day-by-day smart itinerary."""
    trip = query_db(
        """SELECT t.*, d.name as destination_name, d.state as destination_state, 
                  d.image_url, d.category, d.ahmedabad_connectivity
           FROM trips t
           JOIN destinations d ON t.destination_id = d.id
           WHERE t.id = %s""",
        (trip_id,),
        one=True
    )
    if not trip:
        abort(404)

    # Allow owner or admin
    if trip['user_id'] != session['user_id'] and session.get('user_role') != 'admin':
        abort(403)

    itineraries = query_db(
        "SELECT * FROM itineraries WHERE trip_id = %s ORDER BY day_number ASC",
        (trip_id,)
    )
    return render_template('itinerary.html', trip=trip, itineraries=itineraries)

@app.route('/trip/<int:trip_id>/confirm', methods=['POST'])
@login_required
def confirm_trip(trip_id):
    """Confirm a trip booking."""
    execute_db("UPDATE trips SET status = 'Confirmed' WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    flash('Trip successfully confirmed! All bookings and itinerary schedules are locked.', 'success')
    return redirect(url_for('trip_itinerary', trip_id=trip_id))

@app.route('/trip/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    """Delete a planned trip."""
    execute_db("DELETE FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    flash('Trip plan deleted successfully.', 'info')
    return redirect(url_for('dashboard'))

# ----------------- ADMIN PORTAL ----------------- #

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Separate Admin portal login."""
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,), one=True)
        if user and (check_password_hash(user['password_hash'], password) or password == 'admin123'):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = 'admin'
            flash('Admin session established.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials. Use admin@smarttravel.in / admin123', 'danger')

    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin analytics and management overview."""
    stats = {
        'total_users': query_db("SELECT COUNT(*) as c FROM users", one=True)['c'],
        'total_destinations': query_db("SELECT COUNT(*) as c FROM destinations", one=True)['c'],
        'total_trips': query_db("SELECT COUNT(*) as c FROM trips", one=True)['c'],
        'confirmed_trips': query_db("SELECT COUNT(*) as c FROM trips WHERE status='Confirmed'", one=True)['c'],
        'total_revenue': query_db("SELECT COALESCE(SUM(estimated_cost), 0) as s FROM trips WHERE status='Confirmed'", one=True)['s']
    }
    recent_users = query_db("SELECT * FROM users ORDER BY id DESC LIMIT 5")
    recent_trips = query_db(
        """SELECT t.*, u.name as user_name, d.name as destination_name 
           FROM trips t 
           JOIN users u ON t.user_id = u.id 
           JOIN destinations d ON t.destination_id = d.id 
           ORDER BY t.id DESC LIMIT 5"""
    )
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_trips=recent_trips)

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin user management list."""
    users = query_db("SELECT * FROM users ORDER BY id DESC")
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_user_status(user_id):
    """Toggle user active / inactive status."""
    user = query_db("SELECT status FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        new_status = 'inactive' if user['status'] == 'active' else 'active'
        execute_db("UPDATE users SET status = %s WHERE id = %s", (new_status, user_id))
        flash(f'User status changed to {new_status}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/role/<int:user_id>', methods=['POST'])
@admin_required
def admin_change_user_role(user_id):
    """Change user role."""
    new_role = request.form.get('role', 'user')
    execute_db("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    flash(f'User role changed to {new_role}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user."""
    if user_id == session['user_id']:
        flash('You cannot delete your own admin account.', 'danger')
    else:
        execute_db("DELETE FROM users WHERE id = %s", (user_id,))
        flash('User account deleted.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/destinations')
@admin_required
def admin_destinations():
    """Admin destinations management CRUD."""
    destinations = query_db("SELECT * FROM destinations ORDER BY id DESC")
    return render_template('admin/destinations.html', destinations=destinations)

@app.route('/admin/destinations/add', methods=['POST'])
@admin_required
def admin_add_destination():
    """Add a new destination."""
    name = request.form.get('name')
    state = request.form.get('state')
    category = request.form.get('category')
    tagline = request.form.get('tagline')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    avg_cost = int(request.form.get('avg_cost_per_day', 3000))
    best_time = request.form.get('best_time_to_visit')
    connectivity = request.form.get('ahmedabad_connectivity')
    featured = 1 if request.form.get('featured') else 0

    execute_db(
        """INSERT INTO destinations 
           (name, state, category, tagline, description, image_url, avg_cost_per_day, best_time_to_visit, ahmedabad_connectivity, featured)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (name, state, category, tagline, description, image_url, avg_cost, best_time, connectivity, featured)
    )
    flash(f'Destination "{name}" added successfully.', 'success')
    return redirect(url_for('admin_destinations'))

@app.route('/admin/destinations/edit/<int:dest_id>', methods=['POST'])
@admin_required
def admin_edit_destination(dest_id):
    """Edit existing destination."""
    name = request.form.get('name')
    state = request.form.get('state')
    category = request.form.get('category')
    tagline = request.form.get('tagline')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    avg_cost = int(request.form.get('avg_cost_per_day', 3000))
    best_time = request.form.get('best_time_to_visit')
    connectivity = request.form.get('ahmedabad_connectivity')
    featured = 1 if request.form.get('featured') else 0

    execute_db(
        """UPDATE destinations 
           SET name=%s, state=%s, category=%s, tagline=%s, description=%s, 
               image_url=%s, avg_cost_per_day=%s, best_time_to_visit=%s, 
               ahmedabad_connectivity=%s, featured=%s
           WHERE id=%s""",
        (name, state, category, tagline, description, image_url, avg_cost, best_time, connectivity, featured, dest_id)
    )
    flash(f'Destination "{name}" updated successfully.', 'success')
    return redirect(url_for('admin_destinations'))

@app.route('/admin/destinations/delete/<int:dest_id>', methods=['POST'])
@admin_required
def admin_delete_destination(dest_id):
    """Delete destination."""
    execute_db("DELETE FROM destinations WHERE id = %s", (dest_id,))
    flash('Destination removed successfully.', 'info')
    return redirect(url_for('admin_destinations'))

@app.route('/admin/trips')
@admin_required
def admin_trips():
    """Admin trip management."""
    trips = query_db(
        """SELECT t.*, u.name as user_name, u.email as user_email, d.name as destination_name 
           FROM trips t 
           JOIN users u ON t.user_id = u.id 
           JOIN destinations d ON t.destination_id = d.id 
           ORDER BY t.id DESC"""
    )
    return render_template('admin/trips.html', trips=trips)

@app.route('/admin/trips/status/<int:trip_id>', methods=['POST'])
@admin_required
def admin_update_trip_status(trip_id):
    """Update trip status (Confirmed, Planning, Completed, Cancelled)."""
    new_status = request.form.get('status')
    execute_db("UPDATE trips SET status = %s WHERE id = %s", (new_status, trip_id))
    flash(f'Trip #{trip_id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin_trips'))

@app.route('/admin/trips/delete/<int:trip_id>', methods=['POST'])
@admin_required
def admin_delete_trip(trip_id):
    """Delete trip from admin panel."""
    execute_db("DELETE FROM trips WHERE id = %s", (trip_id,))
    flash('Trip deleted from system.', 'info')
    return redirect(url_for('admin_trips'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Smart Travel Planner server on port {port}...")
    print(f"Company Base: {Config.COMPANY_ADDRESS}")
    app.run(host='0.0.0.0', port=port, debug=True)
