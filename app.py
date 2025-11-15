from flask import Flask, render_template, request, session, redirect, url_for
import os

# Initialize the Flask app
app = Flask(__name__)

# A secret key is required for sessions (which store user progress)
app.secret_key = os.urandom(24)

# Define the secret phone number
SECRET_PHONE = "7358647144"

# Helper function to get ordinal numbers (1st, 2nd, 3rd)
def get_ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Main route to start or restart the game
@app.route('/')
def index():
    # Reset game progress in the session
    session['current_index'] = 0
    session['digits_guessed'] = []
    return redirect(url_for('game'))

# The main game route, handles both GET (loading) and POST (guessing)
@app.route('/game', methods=['GET', 'POST'])
def game():
    message = ""
    message_class = ""

    if request.method == 'POST':
        guess = request.form.get('guess')
        
        # Check if the guess is a single digit
        if guess and guess.isdigit() and len(guess) == 1:
            current_index = session.get('current_index', 0)
            correct_digit = SECRET_PHONE[current_index]

            if guess == correct_digit:
                # --- CORRECT GUESS ---
                session['digits_guessed'].append(guess)
                session['current_index'] += 1
                session.modified = True  # Tell Flask the session has changed
                
                # Check for win condition
                if session['current_index'] == len(SECRET_PHONE):
                    return redirect(url_for('win'))
                
                message = "Correct! Keep going."
                message_class = "correct"
            else:
                # --- WRONG GUESS ---
                message = "Wrong! Try that digit again."
                message_class = "wrong"
        else:
            message = "Please enter a single digit (0-9)."
            message_class = "wrong"

    # --- Prepare variables for the template (for GET requests or after a POST) ---
    current_index = session.get('current_index', 0)
    guessed_part = "".join(session.get('digits_guessed', []))
    
    # Create the progress display (e.g., "123*****")
    progress_display = guessed_part + "*" * (len(SECRET_PHONE) - current_index)
    
    # Create the prompt (e.g., "Guess the 4th digit:")
    prompt = f"Guess the {get_ordinal(current_index + 1)} digit (0-9):"

    return render_template('index.html', 
                             progress=progress_display, 
                             prompt=prompt, 
                             message=message,
                             message_class=message_class)

# The "You Win" page
@app.route('/win')
def win():
    return render_template('win.html', phone_number=SECRET_PHONE)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)