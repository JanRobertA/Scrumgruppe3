import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
##dette er en test
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Legg til en hemmelig nøkkel for å bruke flash-meldinger

# Konfigurer databasetilkoblingen
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:gokstad@localhost:3306/scrum_gruppe3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Opprett en instans av SQLAlchemy-objektet
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)


# Definer modellen for brukere
class Users(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    fornavn = db.Column(db.String(100), nullable=False)
    etternavn = db.Column(db.String(100), nullable=False)
    epost = db.Column(db.String(255), unique=True, nullable=False)
    passord_hash = db.Column(db.String(255), nullable=False)
    telefonnummer = db.Column(db.String(25))
    adresse = db.Column(db.Text)
    registreringsdato = db.Column(db.Date, nullable=False)
    rolle = db.Column(db.Enum('admin', 'student'), default='student')


# Opprett databasetabellene
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Hovedside
@app.route('/')
def index():
    return render_template('Nettside.html')


# Innloggingsside
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        epost = request.form['epost']
        passord = request.form['passord']
        user = Users.query.filter_by(epost=epost).first()
        if user and check_password_hash(user.passord_hash, passord):
            login_user(user)
            flash('Du er nå logget inn!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Feil e-post eller passord. Vennligst prøv igjen.', 'danger')
    return render_template('login.html')


# Dashboard etter innlogging
@app.route('/dashboard')
@login_required
def dashboard():
    # Du kan legge til innhold for dashboard-siden her
    return "Dette er dashboard-siden etter vellykket innlogging."


# Utlogging
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du er nå logget ut.', 'success')
    return redirect(url_for('login'))


# Registreringsside
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fornavn = request.form['fornavn']
        etternavn = request.form['etternavn']
        epost = request.form['epost']
        passord = request.form['passord']
        telefonnummer = request.form['telefonnummer']
        adresse = request.form['adresse']

        hashed_password = generate_password_hash(passord)  # Generer passordhash

        # Opprett en ny bruker i databasen
        new_user = Users(fornavn=fornavn, etternavn=etternavn, epost=epost,
                        passord_hash=hashed_password, telefonnummer=telefonnummer,
                        adresse=adresse, registreringsdato='2024-04-11')
        db.session.add(new_user)
        db.session.commit()
        print(new_user)

        flash('Bruker opprettet vellykket! Du kan nå logge inn.')
        return redirect(url_for('login'))  # Omdiriger til logg inn siden

    return render_template('register.html')


# Om oss side
@app.route('/about')
def about():
    # Rendrer malen about.html med den spesifikke meldingen
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
