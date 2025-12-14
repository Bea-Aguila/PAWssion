from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from forms import UserRegisterForm, ShelterRegisterForm, LoginForm, AnimalForm, AdoptionForm, UserInfoForm
from models import db, User, Shelter, Animal, AdoptionRequest, Notification
# ---------------------- Flask Setup ----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///pawssion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

db.init_app(app)

# ---------------------- Index ----------------------
# route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# ---------------------- User Registration ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        # I-check kung existing na ang email sa User o Shelter
        existing_email = User.query.filter_by(email=request.form['email']).first() \
                 or Shelter.query.filter_by(email=request.form['email']).first()
        if existing_email:
            flash("Email already exists! Please use a different email.")
            return redirect(url_for('register'))
        
        # Check username uniqueness
        existing_username = User.query.filter_by(username=request.form['username']).first()
        if existing_username:
            flash("Username already exists! Please choose a different username.")
            return redirect(url_for('register'))

        # Hash the password bago i-save sa database para mas secure
        hashed_pw = generate_password_hash(request.form['password'])

        # get user information in user registration form
        user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            username=request.form['username'],
            email=request.form['email'],
            password=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        # notification for new users
        note_user = Notification(
            message="Account created successfully. Welcome!",
            user_id=user.id
        )
        db.session.add(note_user)
        db.session.commit()

        flash('Account created! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def user_profile():
    user = User.query.get(session['user_id'])
    form = UserInfoForm(obj=user)  # populate form with existing info

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.email = form.email.data
        user.age = form.age.data
        user.gender = form.gender.data
        user.address = form.address.data
        user.contact = form.contact.data
        db.session.commit()
        flash("Profile updated!")
        return redirect(url_for('user_profile'))

    return render_template('user_profile.html', form=form, user=user)

# ---------------------- Shelter Registration ----------------------
@app.route('/shelter_register', methods=['GET', 'POST'])
def shelter_register():
    form = ShelterRegisterForm()
    if form.validate_on_submit():
        website = form.website.data or None

        rejected_shelter = Shelter.query.filter_by(email=request.form['email'], approved=False).first()
        if rejected_shelter:
            db.session.delete(rejected_shelter)
            db.session.commit()
    
        existing_email_user = User.query.filter_by(email=request.form['email']).first()
        existing_email_shelter = Shelter.query.filter(
            Shelter.email == request.form['email'],
            Shelter.approved != False  # ignore rejected shelters
        ).first()

        if existing_email_user or existing_email_shelter:
            flash("Email already exists! Please use a different email.")
            return redirect(url_for('shelter_register'))


        hashed_pw = generate_password_hash(request.form['password'])
        # Getting data in the form and save it to the database
        shelter = Shelter(
            name=request.form['name'],
            description=request.form['description'],
            address=request.form['address'],
            contact_number=request.form['contact_number'],
            email=request.form['email'],
            website=website,
            password=hashed_pw,   
            date_established=request.form['date_established'],
            shelter_type=request.form['shelter_type'],
            approved=None
        )
        db.session.add(shelter)
        db.session.commit()

        # Notify admin about new shelters
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            note = Notification(
                message=f"New shelter registered: {shelter.name}. Pending approval.",
                user_id=admin_user.id
            )
            db.session.add(note)
            db.session.commit()

        flash("Shelter registered! Waiting for admin approval.")
        return redirect(url_for('index'))
    return render_template('shelter_register.html', form=form)

# ---------------------- Login ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if User/Admin
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('admin_dashboard') if user.role=='admin' else url_for('user_dashboard'))

        # Check if Shelter
        shelter = Shelter.query.filter_by(email=email).first()
        if shelter and check_password_hash(shelter.password, password):
            if shelter.approved is True:
        # Shelter approved - login successful
                session['user_id'] = shelter.id
                session['role'] = 'shelter'
                return redirect(url_for('shelter_dashboard'))
            elif shelter.approved is False:
                # Shelter rejected - show message
                flash("Your previous registration was rejected. You can register again.", "danger")
                return redirect(url_for('login'))
            else:
                # Shelter pending - show pending message
                flash("Your shelter account is pending admin approval.", "warning")
                return render_template('login.html', form=form)

        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

# ---------------------- Logout ----------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

# ---------------------- Dashboards ----------------------
@app.route('/shelter_dashboard')
def shelter_dashboard():
    if session.get('role') != 'shelter':
        flash("Access denied!")
        return redirect(url_for('login'))

    shelter_id = session['user_id']
    shelter = Shelter.query.get(shelter_id)
    animals = Animal.query.filter_by(shelter_id=shelter_id).all()
    pending_requests = AdoptionRequest.query.join(Animal).filter(
        Animal.shelter_id == shelter_id,
        AdoptionRequest.status == 'pending'
    ).all()
    notifications = Notification.query.filter_by(shelter_id=shelter_id).order_by(Notification.timestamp.desc()).all()
    unread_count = Notification.query.filter_by(shelter_id=shelter_id, read=False).count()

    # --- NEW: animal_status & animal_adopter ---
    animal_status = {}
    animal_adopter = {}
    for a in animals:
        approved = AdoptionRequest.query.filter_by(animal_id=a.id, status='approved').first()
        if approved:
            animal_status[a.id] = 'Adopted'
            animal_adopter[a.id] = f"{approved.user.first_name} {approved.user.last_name}"  # name ng user
        else:
            animal_status[a.id] = 'Available'
            animal_adopter[a.id] = None

    return render_template('shelter_dashboard.html', user=shelter, animals=animals,
                           pending_requests=pending_requests, notifications=notifications, 
                           unread_count=unread_count, animal_status=animal_status, animal_adopter=animal_adopter)

@app.route('/user_dashboard')
def user_dashboard():
    # Check kung naka-login bilang user
    if session.get('role') != 'user':
        flash("Access denied!")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # Kunin lahat ng approved shelters para makita ng user
    shelters = Shelter.query.filter_by(approved=True).all()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.timestamp.desc()).all()

    # Count unread notifications
    unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
    return render_template('user_dashboard.html', user=user, shelters=shelters, notifications=notifications, unread_count=unread_count)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied!")
        return redirect(url_for('login'))
    
    admin_id = session['user_id']

    # Get all the notifications for admin only
    notifications = Notification.query.filter_by(user_id=admin_id).order_by(Notification.timestamp.desc()).all()
    unread_count = Notification.query.filter_by(user_id=admin_id, read=False).count()

    return render_template('admin_dashboard.html', notifications=notifications, unread_count=unread_count)

# ---------------------- Notifications ----------------------
@app.route('/notifications')
def notifications():
    role = session.get('role')
    user_id = session.get('user_id')

    if role not in ['user', 'shelter', 'admin']:
        flash("Access denied!")
        return redirect(url_for('login'))

    # Map roles to the correct filter key
    filter_key = 'user_id' if role in ['user', 'admin'] else 'shelter_id'

    notifications = Notification.query.filter_by(**{filter_key: user_id})\
                                      .order_by(Notification.timestamp.desc())\
                                      .all()
    
    for note in notifications:
        if not note.read:
            note.read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)

# ---------------------- Admin Managing new Shelters ----------------------
@app.route('/admin/approved_shelters')
def admin_approved_shelters():
    if session.get('role') != 'admin':
        flash("Access denied!")
        return redirect(url_for('index'))
    shelters = Shelter.query.filter_by(approved=True).all()
    return render_template('admin_approved_shelters.html', shelters=shelters)

@app.route('/admin/pending_shelters')
def admin_pending_shelters():
    if session.get('role') != 'admin':
        flash("Access denied!")
        return redirect(url_for('index'))
    
    # Kunin lahat ng shelters na hindi pa approved
    shelters = Shelter.query.filter_by(approved=None).all()
    return render_template('admin_pending_shelters.html', shelters=shelters)

@app.route('/admin/view_shelter/<int:shelter_id>')
def admin_view_shelter(shelter_id):
    if session.get('role') != 'admin':
        flash("Access denied!")
        return redirect(url_for('index'))
    shelter = Shelter.query.get_or_404(shelter_id)
    return render_template('admin_view_shelter.html', shelter=shelter)

@app.route('/admin/approve_shelter/<int:shelter_id>', methods=['POST'])
def approve_shelter(shelter_id):
    if session.get('role') != 'admin':
        flash("Access denied!")
        return redirect(url_for('index'))

    shelter = Shelter.query.get_or_404(shelter_id)
    shelter.approved = True
    db.session.commit()

    # Notify admin
    admin_user = User.query.filter_by(role='admin').first()
    if admin_user:
        note = Notification(
            message=f"Approved Shelter: {shelter.name}.",
            user_id=admin_user.id
        )
        db.session.add(note)
        db.session.commit()

    # Notify shelter
    notif = Notification(
        message="Your shelter has been approved! You can now log in and access your dashboard.",
        shelter_id=shelter.id
    )
    db.session.add(notif)
    db.session.commit()

    flash("Shelter approved!")
    return redirect(url_for('admin_approved_shelters'))

@app.route('/admin/reject_shelter/<int:shelter_id>', methods=['POST'])
def reject_shelter(shelter_id):
    if session.get('role') != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))

    shelter = Shelter.query.get_or_404(shelter_id)

    # Mark as rejected
    shelter.approved = False
    db.session.commit()

    # Notify admin
    admin_user = User.query.filter_by(role='admin').first()
    if admin_user:
        note = Notification(
            message=f"Shelter rejected: {shelter.name}.",
            user_id=admin_user.id
        )
        db.session.add(note)
        db.session.commit()

    flash(f"{shelter.name} has been rejected.", "danger")
    return redirect(url_for('admin_pending_shelters'))


@app.route('/admin/delete_shelter/<int:shelter_id>', methods=['POST'])
def delete_shelter(shelter_id):
    if session.get('role') != 'admin':
        flash("Access denied!")
        return redirect(url_for('index'))

    shelter = Shelter.query.get_or_404(shelter_id)

    # Delete all adoption requests for animals of this shelter
    animals = Animal.query.filter_by(shelter_id=shelter.id).all()
    for animal in animals:
        # Notify users whose adoption requests will be deleted
        adoption_requests = AdoptionRequest.query.filter_by(animal_id=animal.id).all()
        for req in adoption_requests:
            db.session.add(Notification(
                user_id=req.user_id,
                message=f"Your adoption request for {animal.name} has been canceled because the shelter '{shelter.name}' was deleted."
            ))
            db.session.delete(req)  # Delete the adoption request

        # Delete the animal
        db.session.delete(animal)

    # Notify admin about the deletion
    admin_user = User.query.filter_by(role='admin').first()
    if admin_user:
        db.session.add(Notification(
            user_id=admin_user.id,
            message=f"The shelter '{shelter.name}' and all its animals were successfully deleted."
        ))

    # Finally, delete the shelter
    db.session.delete(shelter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# ---------------------- Shelter Adoption ----------------------
@app.route('/shelter/adoption_requests')
def shelter_adoption_requests():
    if session.get('role') != 'shelter':
        flash("Access denied!")
        return redirect(url_for('index'))

    shelter_id = session['user_id']
    # Query all pending adoption requests for animals belonging to this shelter
    pending_requests = AdoptionRequest.query.join(Animal).filter(
        Animal.shelter_id == shelter_id,
        AdoptionRequest.status == 'pending'
    ).all()
    return render_template('shelter_adoption_requests.html', pending_requests=pending_requests)

# ---------------------- Shelter Approved Adoption Requests ----------------------
@app.route('/shelter/approved_adoptions')
def shelter_approved_adoptions():
    if session.get('role') != 'shelter':
        flash("Access denied!")
        return redirect(url_for('login'))

    shelter_id = session['user_id']
    approved_adoptions = AdoptionRequest.query.join(Animal).filter(
        Animal.shelter_id == shelter_id,
        AdoptionRequest.status == 'approved'
    ).order_by(AdoptionRequest.timestamp.desc()).all()
    return render_template('approved_adoption.html', approved_adoptions=approved_adoptions)

# ---------------------- View Details of a Specific detail Adoption Request in Pending ----------------------
@app.route('/shelter/adoption_request/<int:request_id>')
def adoption_request_detail(request_id):
    if session.get('role') != 'shelter':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))

    adoption = AdoptionRequest.query.get_or_404(request_id) # get adoption request

    # Ensure that the adoption request belongs to the logged-in shelter
    if adoption.animal.shelter_id != session['user_id']:
        flash("Access denied!", "danger")
        return redirect(url_for('shelter_adoption_requests'))

    return render_template('adoption_request_detail.html', adoption=adoption)

# ---------------------- View a Specific Details of Approved Adoption ----------------------
@app.route('/shelter/approved_adoption/<int:request_id>')
def shelter_view_approved_adoption(request_id):
    if session.get('role') != 'shelter':
        flash("Access denied!")
        return redirect(url_for('login'))

    shelter_id = session['user_id']
    adoption = AdoptionRequest.query.get_or_404(request_id)

     # Ensure the adoption belongs to this shelter AND is approved
    if adoption.animal.shelter_id != shelter_id or adoption.status != 'approved':
        flash("Access denied!")
        return redirect(url_for('shelter_approved_adoptions'))

    return render_template('adoption_request_detail.html', adoption=adoption)

# ---------------------- Shelter Approve or Reject an Adoption Request ----------------------
@app.route('/shelter/approve_adoption/<int:request_id>', methods=['POST'])
def shelter_approve_adoption(request_id):
    if session.get('role') != 'shelter':
        flash("Unauthorized!")
        return redirect(url_for('index'))

    shelter_id = session['user_id']
    adoption = AdoptionRequest.query.get_or_404(request_id)

    # Ensure the request belongs to this shelter
    if adoption.animal.shelter_id != shelter_id:
        flash("Access denied!")
        return redirect(url_for('shelter_dashboard'))

    # 1. Approve the selected request
    adoption.status = "approved"

    animal = adoption.animal  # Para madaling gamitin

    # 2. Find OTHER pending requests for the same animal
    other_requests = AdoptionRequest.query.filter(
        AdoptionRequest.animal_id == animal.id,
        AdoptionRequest.id != adoption.id,
        AdoptionRequest.status == "pending"
    ).all()

    # 3. Cancel all other requests + send notification to each user
    for req in other_requests:
        req.status = "canceled"

        db.session.add(Notification(
            user_id=req.user_id,
            message=f"Dear {adoption.animal.shelter.name}, your adoption request for {animal.name} was cancelled as another request was approved."
        ))

    # 4. Notify the approved user
    db.session.add(Notification(
        user_id=adoption.user_id,
        message=f"Your adoption request for {animal.name} was APPROVED by {animal.shelter.name}."
    ))

    db.session.commit()

    flash("Adoption approved. Other requests have been automatically canceled and notified.")
    return redirect(url_for('shelter_adoption_requests'))


@app.route('/shelter/reject_adoption/<int:request_id>', methods=['POST'])
def shelter_reject_adoption(request_id):
    if session.get('role') != 'shelter':
        flash("Unauthorized!")
        return redirect(url_for('index'))

    shelter_id = session['user_id']
    adoption = AdoptionRequest.query.get_or_404(request_id)
    if adoption.animal.shelter_id != shelter_id:
        flash("Access denied!")
        return redirect(url_for('shelter_dashboard'))

    adoption.status = "rejected"  # Set status to rejected

    # Create a notification for the user
    db.session.add(Notification(
        user_id=adoption.user_id,
        message=f"Your adoption request for {adoption.animal.name} was REJECTED by {adoption.animal.shelter.name} shelter."
    ))
    db.session.commit()
    flash("Adoption rejected.")
    return redirect(url_for('shelter_adoption_requests'))

# ---------------------- Adoption by User ----------------------
@app.route('/adopt/<int:animal_id>', methods=['GET','POST'])
def adopt(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    user = User.query.get(session['user_id'])
    form = AdoptionForm()  # kung gusto mo i-display

    # Check if essential info is filled
    required_fields = [user.age, user.address, user.contact, user.gender]
    if not all(required_fields):
        flash("Please complete your profile information before submitting an adoption request.", "warning")
        return redirect(url_for('user_profile'))


    # Check if already submitted a request for this animal
    existing_request = AdoptionRequest.query.filter_by(
        user_id=user.id,
        animal_id=animal.id
    ).first()

    if existing_request:
        flash("You have already submitted an adoption request for this animal.")
        return redirect(url_for('user_dashboard'))

    # Create new adoption request
    if request.method == 'POST':
        adoption = AdoptionRequest(
            user_id=user.id,
            animal_id=animal.id,
            status='pending',
            reason=request.form.get('reason')
        )
        db.session.add(adoption)

        # Notify the shelter about the new adoption request
        db.session.add(Notification(
            message=f"{user.first_name} {user.last_name} requested to adopt {animal.name or animal.type}",
            shelter_id=animal.shelter.id
        ))

        db.session.add(Notification(
            user_id=user.id,
            message=f"Your adoption request for {animal.name} has been submitted and is now pending approval."
        ))

        db.session.commit()
        flash("Adoption request submitted!")
        return redirect(url_for('user_dashboard'))

    return render_template('adoption_form.html', user=user, form=form, animal=animal)


# ---------------------- Post/Edit/Delete Animal (Shelter Dashboard) ----------------------
@app.route('/post_animal', methods=['GET', 'POST'])
def post_animal():
    form = AnimalForm()
    if form.validate_on_submit():
        file = request.files.get('image1')  # Get uploaded file
        if not file or not file.filename:
            flash("Please upload an image!")
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save image

        # Creating new animal record
        animal = Animal(
            name=form.name.data,
            age=form.age.data,
            breed=form.breed.data,
            gender=form.gender.data,
            type=form.type.data,
            description=form.description.data,
            image1=filename,
            shelter_id=session['user_id']   # Link animal to logged-in shelter
        )
        db.session.add(animal)
        db.session.commit()
        flash("Animal posted successfully!")
        return redirect(url_for('shelter_dashboard'))
    return render_template('animal_form.html', form=form)

@app.route('/edit_animal/<int:animal_id>', methods=['GET','POST'])
def edit_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.shelter_id != session['user_id']:
        flash("Access denied!")
        return redirect(url_for('shelter_dashboard'))

    form = AnimalForm()
    if form.validate_on_submit():
        file = request.files.get('image1')   # Handle new image
        if not file or not file.filename:
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        animal.image1 = filename   # Update image

        # Update other details
        animal.name = form.name.data
        animal.age = form.age.data
        animal.type = form.type.data
        animal.breed = form.breed.data
        animal.gender = form.gender.data
        animal.description = form.description.data
        db.session.commit()
        flash("Animal updated successfully.", "success")
        return redirect(url_for('shelter_dashboard'))

    # pre-fill form fields with current animal data
    form.name.data = animal.name
    form.age.data = animal.age
    form.type.data = animal.type
    form.breed.data = animal.breed
    form.gender.data = animal.gender
    form.description.data = animal.description

    return render_template('animal_form.html', form=form, animal=animal)

@app.route('/delete_animal/<int:animal_id>')
def delete_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.shelter_id != session.get('user_id'):
        flash("Access denied!", "danger")
        return redirect(url_for('shelter_dashboard'))

    # I-check kung may existing na APPROVED adoption para sa animal
    approved_request = AdoptionRequest.query.filter_by(animal_id=animal.id, status='approved').first()
    if approved_request:
        flash("This animal already has an APPROVED adoption. Cannot delete.", "warning")
        return redirect(url_for('shelter_dashboard'))

    # Kung wala pang approved adoption, delete ang lahat ng adoption requests sa animal
    AdoptionRequest.query.filter_by(animal_id=animal.id).delete()
    db.session.delete(animal)
    db.session.commit()
    flash("Animal deleted successfully.", "success")
    return redirect(url_for('shelter_dashboard'))

# -----------------Viewing Shelter List in user Dashboard---------------------
@app.route('/shelter_list')
def shelter_list():
    if session.get('role') != 'user':
        flash("Access denied!")
        return redirect(url_for('index'))
    shelters = Shelter.query.filter_by(approved=True).all()
    return render_template('shelter_list.html', shelters=shelters)

# ---------------------- Animal Flip View for User ---------------------------
@app.route('/view_shelter/<int:shelter_id>/<string:animal_type>')
def view_shelter_type(shelter_id, animal_type):
    if 'user_id' not in session:
        flash("Please log in to view animals.")
        return redirect(url_for('login'))

    shelter = Shelter.query.get_or_404(shelter_id)

    # Get all animals of this type
    animals = Animal.query.filter(
        Animal.shelter_id == shelter.id,
        db.func.lower(Animal.type) == animal_type.lower()
    ).all()

    animal_status = {}   # 'Available' or 'Adopted'
    animal_adopter = {}  # user_id of the adopter

    for a in animals:
        approved_request = AdoptionRequest.query.filter_by(animal_id=a.id, status='approved').first()
        if approved_request:
            animal_status[a.id] = 'Adopted'
            animal_adopter[a.id] = approved_request.user_id
        else:
            animal_status[a.id] = 'Available'
            animal_adopter[a.id] = None

    return render_template(
        'animal_flip_view.html',
        shelter=shelter,
        animals=animals,
        animal_type=animal_type,
        animal_status=animal_status,
        animal_adopter=animal_adopter
    )

@app.route('/view_animal/<int:animal_id>')
def view_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)

    # I-check kung adopted na ang animal
    approved_request = AdoptionRequest.query.filter_by(animal_id=animal.id, status='approved').first()
    status = 'Adopted' if approved_request else 'Available'
    return render_template('animal_detail.html', animal=animal, status=status)

# User Adoption Requests List
@app.route('/my_adoption_requests')
def user_adoption_requests():
    if session.get('role') != 'user':
        flash("Access denied!")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    # Only show pending and approved requests
    requests = AdoptionRequest.query.filter(
        AdoptionRequest.user_id == user_id,
        AdoptionRequest.status.in_(["pending", "approved"])
    ).all()
    
    return render_template('user_adoption_requests.html', requests=requests)


# View single request details
@app.route('/adoption_request/<int:request_id>')
def view_adoption_request(request_id):
    # Ensure only this user and only pending/approved requests
    req = AdoptionRequest.query.filter(
        AdoptionRequest.id == request_id,
        AdoptionRequest.user_id == session.get('user_id'),
        AdoptionRequest.status.in_(["pending", "approved"])
    ).first_or_404()

    return render_template('view_adoption_request.html', request=req)


# Cancel a request (like deleting it)
@app.route('/cancel_adoption_request/<int:request_id>', methods=['POST'])
def cancel_adoption_request(request_id):
    req = AdoptionRequest.query.get_or_404(request_id)

    if req.user_id != session.get('user_id'):
        flash("Access denied!")
        return redirect(url_for('user_dashboard'))

    if req.status == 'approved':
        flash("This adoption request has been approved and cannot be canceled.")
        return redirect(url_for('user_adoption_requests'))

    # Delete the request
    db.session.delete(req)
    db.session.commit()

    flash("Your adoption request has been cancelled.")
    return redirect(url_for('user_adoption_requests'))

# ---------------------- Initialize DB ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # default admin
        if not User.query.filter_by(email='admin@pawssion.com').first():
            admin_user = User(
                username="admin",
                email="admin@pawssion.com",
                password=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()

    app.run(debug=True)