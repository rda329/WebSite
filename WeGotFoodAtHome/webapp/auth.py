from flask import Blueprint
from flask import render_template, request, redirect, session, url_for
from .models import store_in_db, get_id_by_email, check_user_login, get_user_fname, get_verify_status, verify_status, change_password, get_token_by_user_id, update_token
from .send_email import send_verify

auth = Blueprint('auth', __name__)



@auth.route('/signin', endpoint = "signin")
def signin():
    display = "sign_in"
    return render_template("login_signup.html", display=display)

@auth.route('/signup', endpoint="signup")
def signup():
    display = "sign_up"
    return render_template("login_signup.html", display=display)

@auth.route('/log_out', endpoint = "logout")
def logout():
    return "logged out"

@auth.route('/user_authentication' , methods=['POST'], endpoint = "authentication")
def user_authentication():
    display = "sign_in"
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == "": 
            alert = "Please enter a valid email."
            return render_template("login_signup.html", display=display, alert=alert)
        elif password == "":
            alert = "Please enter a valid password."
            return render_template("login_signup.html", display=display, alert=alert)
        else:
            check = check_user_login(email,password)
            if check == True:
                user_id = get_id_by_email(email)
                session["user_id"] = user_id
                fname = get_user_fname(user_id)
                session["fname"] = fname
                verify_status = get_verify_status(user_id)
                if verify_status == 1:
                    session["logged_in"] = True
                    return redirect("/thekitchen")
                else:
                    return render_template("verify.html")
            else:
                alert = "The credentials entered were not found on record."
                return render_template("login_signup.html", display=display, alert=alert)
    return "No post"

@auth.route('/user_registration' , methods=['POST'], endpoint="registration")
def user_registration():
    display = "sign_up"
    alert = ""
    if request.method == "POST":
        fname = request.form.get("fname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if len(email) < 4 or email == "":
            alert = "Please enter a valid email."
        elif password1 != password2:
            alert = "Passwords Do Not Match."
        elif password1 == "":
            alert = "Please enter a password."
        else:
            # Add user to db
            user_id = get_id_by_email(email)
            if user_id:
                return render_template("login_signup.html", display=display, alert="An account with the email already exists.")
            else:
                store_in_db(fname=fname, email=email, password=password1)
                user_id = get_id_by_email(email)
                token = get_token_by_user_id(user_id)
                url = url_for('auth.verify', email=email, token=token, _external=True)  # Use 'auth.verify'
                message = "Click on this link to verify your email for The Kitchen"
                send_verify(email,url,message)
                session["user_id"] = user_id
                session["fname"] = fname
                update_token(user_id)
                return render_template("verify.html")
    return render_template("login_signup.html", display=display, alert=alert)

    

@auth.route('/verify_email/<email>/<token>', endpoint="verify")
def verify_email(email, token):
    display = "sign_in"
    user_id = get_id_by_email(email)
    session["user_id"] = user_id
    verify_status(user_id)
    alert = "Your Account Has Been Verified"
    return render_template("login_signup.html", display=display, alert=alert)


@auth.route('/forgot_password', methods=['GET',"POST"], endpoint= "password_retrieval")
def forgot_password():
    if request.method == "POST":
        email = request.form.get('email')
        user_id = get_id_by_email(email)
        if user_id:
            message = "Click the link below to reset your password."
            token = get_token_by_user_id(user_id)
            url = url_for('auth.reset_password', email=email, token=token, _external=True)
            send_verify(email,url,message)
            update_token(user_id)
            return render_template('password_change_email.html')
        else:
            return render_template('forgot_password.html', alert="This email does not exist in our records.")
    else:
        return render_template('forgot_password.html')
 
    
@auth.route('/reset_password/<email>/<token>', methods = ['GET', 'POST'], endpoint = "reset_password")
def reset_password(email,token):
    if request.method == "POST":
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            alert = "Passwords Do Not Match."
            return render_template('reset_password.html', email=email, token=token,alert=alert)
        elif password1 == "":
            alert = "Please enter a password."
            return render_template('reset_password.html', email=email,token=token, alert=alert)
        else:
            change_password(email, password1)
            return render_template('password_change_success.html')
    else:
        return render_template('reset_password.html', email=email, token=token)
