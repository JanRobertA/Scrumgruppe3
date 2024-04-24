from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurer databasetilkoblingen
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:gokstad@localhost:3306/scrum_gruppe3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Opprett en instans av SQLAlchemy-objektet
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)


def get_time_greeting():
    now = datetime.now()
    if 5 <= now.hour < 12:
        return "God morgen!"
    elif 12 <= now.hour < 18:
        return "God ettermiddag!"
    else:
        return "God kveld!"


# Definer modellen for brukere
class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, primary_key=True)
    fornavn = db.Column(db.String(100), nullable=False)
    etternavn = db.Column(db.String(100), nullable=False)
    epost = db.Column(db.String(255), unique=True, nullable=False)
    passord_hash = db.Column(db.String(255), nullable=False)
    telefonnummer = db.Column(db.String(25))
    adresse = db.Column(db.Text)
    registreringsdato = db.Column(db.Date, nullable=False)
    rolle = db.Column(db.Enum('admin', 'student'), default='student')
    reviews = relationship('Review', backref='user', lazy='dynamic')
    loans = db.relationship('Loans', backref='user', lazy='dynamic')

    # Implementer get_id-metoden
    def get_id(self):
        return str(self.user_id)


# Definer modellen for bøker
class Books(db.Model):
    __tablename__ = 'books'
    __table_args__ = {'extend_existing': True}
    book_id = db.Column(db.Integer, primary_key=True)
    tittel = db.Column(db.String(255), nullable=False)
    forfatter = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    utgivelsesår = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(100))
    status = db.Column(db.Enum('Tilgjengelig', 'Utlånt', 'Forsinket'), default='Tilgjengelig')
    reviews = relationship('Review', backref='book', lazy='dynamic')


class Loans(db.Model):
    loan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    utlånsdato = db.Column(db.Date, nullable=False)
    forventet_returdato = db.Column(db.Date, nullable=False)
    faktisk_returdato = db.Column(db.Date)
    status = db.Column(db.Enum('Aktiv', 'Fullført', 'Forsinket'), default='Aktiv')
    reminder_sent = db.Column(db.Enum('Ja', 'Nei'), default='Nei')

    # Legg til relasjon til Books-modellen
    book = db.relationship('Books', backref='loan', lazy=True)

    # Implementer get_id-metoden
    def get_id(self):
        return str(self.user_id)


# Modell for påminnelser
class Reminders(db.Model):
    reminder_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.loan_id'))
    purringsdato = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Sendt', 'Ikke Sendt'), default='Ikke Sendt')
    melding = db.Column(db.Text)
    lest = db.Column(db.Boolean)


# Opprett databasetabellene
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Hovedside
@app.route('/')
def index():
    greeting = get_time_greeting()
    return render_template('Nettside.html', greeting=greeting)


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
            if user.rolle == 'admin':
                return redirect(url_for('admin'))
            elif user.rolle == 'student':
                return redirect(url_for('bibliotek'))
            else:
                flash('Ugyldig rolle for bruker.', 'danger')
        else:
            flash('Feil e-post eller passord. Vennligst prøv igjen.', 'danger')
    return render_template('login.html')


# Adminside
@app.route('/admin')
@login_required
def admin():
    if current_user.rolle == 'admin':
        greeting = get_time_greeting()
        return render_template('admin.html', navn=current_user.fornavn, greeting=greeting)
    else:
        flash('Du har ikke tilgang til denne siden.', 'danger')
        return redirect(url_for('index'))


# Bibliotekside
@app.route('/bibliotek')
@login_required
def bibliotek():
    if current_user.rolle == 'student' or current_user.rolle == 'admin':
        greeting = get_time_greeting()
        # Hent aktive lån og tilhørende purringer fra databasen
        active_loans = Loans.query.filter_by(status='Aktiv', reminder_sent='Nei').all()
        reminders = Reminders.query.filter_by(status='Sendt', lest=0).all()

        return render_template('bibliotek.html', navn=current_user.fornavn, greeting=greeting,
                               active_loans=active_loans, reminders=reminders)
    else:
        flash('Du har ikke tilgang til denne siden.', 'danger')
        return redirect(url_for('index'))


@app.route('/read_reminder', methods=['GET', 'POST'])
def read_reminder():
    if request.method == 'POST':
        # Get the reminder_id from the form submission
        reminder_id = request.form.get('reminder_id')
        reminder = Reminders.query.get(reminder_id)

        if reminder:
            # Update the reminder
            reminder.lest = 1
            db.session.commit()

            # Redirect to another endpoint, for example 'bibliotek'
            return redirect(url_for('bibliotek'))

    # Handle GET requests if needed
    # You may want to return some kind of response here
    return 'Method not allowed'


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

        flash('Bruker opprettet vellykket! Du kan nå logge inn.')
        return redirect(url_for('login'))  # Omdiriger til logg inn siden

    return render_template('register.html')


# Om oss side
@app.route('/about')
def about():
    return render_template('about.html')


# Legg til dine ruter for Purringer og Brukere her

@app.route('/Purringer', methods=['GET', 'POST'])
@login_required
def purringer():
    if current_user.rolle == 'admin':
        if request.method == 'POST':
            loan_id = request.form.get('loan_id')
            message = request.form.get('message')  # Legg til mottak av meldingen fra skjemaet
            send_reminder(loan_id, message)  # Endret til å sende meldingen med påminnelsen

            # Lagre purringen i databasen
            loan = Loans.query.get(loan_id)
            if loan:
                new_reminder = Reminders(loan_id=loan_id, purringsdato=datetime.now(), status='Ikke Sendt',
                                         melding=message)
                db.session.add(new_reminder)
                db.session.commit()

            flash('Purringsmelding sendt til brukeren.', 'success')
            return redirect(url_for('Purringer'))
        else:
            active_loans = Loans.query.filter_by(status='Aktiv', reminder_sent='Nei').all()
            for loan in active_loans:
                print(loan.user.fornavn, loan.user.etternavn, loan.book.tittel)
            return render_template('Purringer.html', active_loans=active_loans)
    else:
        flash('Du har ikke tilgang til denne siden.', 'danger')
        return redirect(url_for('index'))


@app.route('/Brukere')
def brukere():
    student_users = Users.query.filter_by(rolle='student').all()
    return render_template('brukere.html', student_users=student_users)


# Resten av koden for Litteratur_oversikt, sletting og endring av litteratur, utlån, retur, og anmeldelser forblir uendret


@app.route('/Litteratur_oversikt')
def litteratur_oversikt():
    # Hent alle bøker fra databasen
    books = Books.query.all()
    return render_template('Litteratur_oversikt.html', books=books)


@app.route('/remove_book/<isbn>', methods=['POST'])
@login_required
def remove_book(isbn):
    if current_user.rolle == 'admin':
        book_to_remove = Books.query.filter_by(isbn=isbn).first()
        if book_to_remove:
            db.session.delete(book_to_remove)
            db.session.commit()
            flash('Bok fjernet fra databasen!')
        else:
            flash('Kunne ikke finne boken med angitt ISBN.', 'danger')
    else:
        flash('Du har ikke tilgang til denne funksjonen.', 'danger')
    return redirect(url_for('endre_litteratur'))


# Endre litteratur side
@app.route('/endre_litteratur', methods=['GET', 'POST'])
@login_required
def endre_litteratur():
    if current_user.rolle == 'admin':
        if request.method == 'POST':
            tittel = request.form['tittel']
            forfatter = request.form['forfatter']
            isbn = request.form['isbn']
            utgivelsesår = request.form['utgivelsesår']
            kategori = request.form['kategori']
            new_book = Books(tittel=tittel, forfatter=forfatter, isbn=isbn, utgivelsesår=utgivelsesår,
                             kategori=kategori)
            db.session.add(new_book)
            db.session.commit()
            flash('Bok lagt til i databasen!')
            return redirect(url_for('endre_litteratur'))
        return render_template('endre_litteratur.html')
    else:
        flash('Du har ikke tilgang til denne siden.', 'danger')
        return redirect(url_for('index'))


@app.route('/slette_litteratur', methods=['GET', 'POST'])
@login_required
def slette_litteratur():
    if current_user.rolle == 'admin':
        if request.method == 'POST':
            isbn = request.form['isbn']
            book_to_remove = Books.query.filter_by(isbn=isbn).first()
            if book_to_remove:
                db.session.delete(book_to_remove)
                db.session.commit()
                flash('Bok fjernet fra databasen!')
                return redirect(url_for('slette_litteratur'))
            else:
                flash('Kunne ikke finne boken med angitt ISBN.', 'danger')
                return redirect(url_for('slette_litteratur'))
        return render_template('slette_litteratur.html')
    else:
        flash('Du har ikke tilgang til denne siden.', 'danger')
        return redirect(url_for('index'))


@app.route('/loan_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def loan_book(book_id):
    print("Accessing book with ID:", book_id)  # Debug statement
    book = Books.query.get(book_id)
    if not book:
        print("No book found with ID:", book_id)
        flash('Ingen bok funnet med ID: {}'.format(book_id), 'danger')
        return redirect(url_for('availablebooks'))

    if request.method == 'POST':
        if book.status == 'Tilgjengelig':
            book.status = 'Utlånt'
            new_loan = Loans(user_id=current_user.user_id, book_id=book_id,
                             utlånsdato=datetime.now(),
                             forventet_returdato=datetime.now() + timedelta(days=30))
            db.session.add(new_loan)
            db.session.commit()
            flash('Boken er nå lånt.', 'success')
        else:
            flash('Boken er ikke tilgjengelig.', 'danger')
        return redirect(url_for('availablebooks'))
    else:
        # Håndter GET-forespørsel for å vise bokdetaljer
        return render_template('loan_book.html', book=book)


@app.route('/availablebooks')
def availablebooks():
    # Hent alle tilgjengelige bøker og inkluder gjennomsnittsvurdering hvis tilgjengelig
    books = db.session.query(
        Books.book_id,
        Books.tittel,
        Books.forfatter,
        db.func.round(db.func.avg(Review.vurdering), 1).label('gjennomsnitt_vurdering')
    ).outerjoin(
        Review, Books.book_id == Review.book_id
    ).filter(
        Books.status == 'Tilgjengelig'  # Filtrer kun bøker som er tilgjengelige
    ).group_by(
        Books.book_id
    ).all()

    return render_template('availablebooks.html', books=books)


@app.route('/your_loands')
@login_required
def your_loands():
    loans = Loans.query.filter_by(user_id=current_user.user_id, status='Aktiv').all()
    books = [Books.query.get(loan.book_id) for loan in loans]
    return render_template('your_loands.html', books=books)


@app.route('/process_loan/<int:book_id>', methods=['POST'])
@login_required
def process_loan(book_id):
    book = Books.query.get(book_id)
    if book and book.status == 'Tilgjengelig':
        book.status = 'Utlånt'
        new_loan = Loans(user_id=current_user.user_id, book_id=book_id,
                         utlånsdato=datetime.today(),
                         forventet_returdato=datetime.today() + timedelta(days=30))
        db.session.add(new_loan)
        db.session.commit()
        flash('Du har nå lånt boken.', 'success')
    else:
        flash('Denne boken er ikke lenger tilgjengelig.', 'danger')
    return redirect(url_for('availablebooks'))


@app.route('/return_book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    loan = Loans.query.filter_by(book_id=book_id, user_id=current_user.user_id, status='Aktiv').first()
    if loan:
        loan.status = 'Fullført'
        loan.faktisk_returdato = datetime.now()
        book = Books.query.get(book_id)
        if book:
            book.status = 'Tilgjengelig'
        db.session.commit()
        flash('Boken er levert tilbake.', 'success')
    else:
        flash('Kunne ikke finne den aktive lånen.', 'danger')
    return redirect(url_for('your_loands'))


###########################################################
##################### R E V I E W S #######################
###########################################################

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    vurdering = db.Column(db.Integer, nullable=False)
    anmeldelse = db.Column(db.Text, nullable=False)
    anmeldelsesdato = db.Column(db.Date, nullable=False, default=db.func.current_date())


@app.route('/add_review/<int:book_id>', methods=['GET', 'POST'])
@login_required  # Pass på at brukeren er logget inn
def add_review(book_id):
    book = Books.query.get(book_id)
    if book is None:
        flash("Boken finnes ikke.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        vurdering = request.form.get('vurdering')
        anmeldelse = request.form.get('anmeldelse')

        if not vurdering or not anmeldelse:
            flash("Alle felt må fylles ut.")
            return redirect(url_for('add_review', book_id=book_id))

        review = Review(book_id=book_id, user_id=current_user.user_id, vurdering=vurdering, anmeldelse=anmeldelse)
        db.session.add(review)
        db.session.commit()
        flash("Din anmeldelse er lagret.")
        return redirect(url_for('show_reviews', book_id=book_id))

    # Vis skjema for GET request
    return render_template('add_review.html', book=book)


@app.route('/reviews/<int:book_id>')
def show_reviews(book_id):
    reviews = Review.query.filter_by(book_id=book_id).all()
    return render_template('reviews.html', reviews=reviews, book_id=book_id)


# Metode for å sende påminnelser
def send_reminder(loan_id, message):
    loan = Loans.query.get(loan_id)
    user = Users.query.get(loan.user_id) if loan else None  # Sjekk for None
    book = Books.query.get(loan.book_id) if loan else None  # Sjekk for None
    if loan and user and book:
        # Lag meldingsteksten
        message_text = (
            f"Hei {user.fornavn}!\n\nDette er en purring på at du har lånt boken '{book.tittel}' som skulle vært returnert innen "
            f"{loan.forventet_returdato}.Med vennlig hilsen,\n'Bibliotek Administrasjonen.'\n ' Ha en {get_time_greeting()}'\n{message}")

        # Lagre påminnelsen i databasen
        new_reminder = Reminders(loan_id=loan_id, purringsdato=datetime.now(), status='Sendt',
                                 melding=message_text, lest=0)
        db.session.add(new_reminder)
        db.session.commit()

        # Oppdater lånet for å markere at en purring er sendt
        loan.reminder_sent = 'Ja'
        db.session.commit()

        # Her kan du implementere koden for å faktisk sende e-postmeldingen
        # for eksempel bruk av en e-posttjeneste eller et meldingsbibliotek
        # For testing kan du bare skrive ut meldingen
        print("Purring sendt til brukeren:")
        print(message_text)
    else:
        print("Kunne ikke sende purring. Ufullstendig informasjon.")


from flask import redirect, flash, url_for


@app.route('/send_reminder', methods=['POST'])
@login_required
def send_reminder_route():
    if request.method == 'POST':
        loan_id = request.form.get('loan_id')
        message = request.form.get('message')

        # Sjekk om lånet-ID eller melding mangler
        if not loan_id or not message:
            flash("Feil: Lånet-ID eller melding mangler.", "error")
            return redirect(url_for('purringer'))

        # Bruk loan_id til å sende påminnelsen
        send_reminder(loan_id, message)

        flash("Purring sendt!", "success")
        return redirect(url_for('purringer'))
    else:
        # Hvis forespørselen ikke er en POST-forespørsel, returner en feilmelding
        flash("Feil: Kun POST-forespørsler er tillatt.", "error")
        return redirect(url_for('purringer'))


if __name__ == '__main__':
    app.run(debug=True)
