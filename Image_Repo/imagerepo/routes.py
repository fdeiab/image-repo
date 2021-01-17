"""
author: Fattima Deiab 

This file contains the code to be executed when a user visits a
specfic page or uploads/deletes images.
"""

from flask import render_template, url_for, flash, redirect, request, abort
from imagerepo import app, db, bcrypt
from imagerepo.userForms import registerForm, loginForm
from imagerepo.database import Users, Images
from flask_login import login_user, current_user,logout_user, login_required
import secrets, os, imghdr, PIL
from os import path
from PIL import Image
from datetime import datetime

"""
this route displays the current contents of the image repository
(only images with public view turned on are displayed)
"""
@app.route('/')
@app.route('/home')
def home():
    page = request.args.get("page", 1, type=int)
    images = Images.query.order_by(Images.datePosted.desc()).filter_by(privStatus = False).paginate(page=page, per_page=9)
    date = datetime.now().strftime('%d/%m/%Y %H:%M')
    date = datetime.strptime(date, "%d/%m/%Y %H:%M")
    date = date.strftime('%d/%m/%Y %I:%M %p')
    date += ' MST'
    return render_template('imagedisp.html', images=images, time=date, screen='home')

"""
this route allows users to make an account
"""
@app.route("/register", methods=['GET', 'POST'])
def register():
    userForm = registerForm()
    # if the user entered the required data correctly, add their info into the database
    if userForm.validate_on_submit():
        # hashes the user's password and saves it as a string 
        userpass_hash = bcrypt.generate_password_hash(userForm.user_pass.data).decode('utf-8') 
        newUser = Users(username = userForm.username.data, userEmail = userForm.user_email.data, userPass = userpass_hash)
        db.session.add(newUser)
        db.session.commit()
        flash(f'Account created successfully.\n Welcome {userForm.username.data}! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=userForm)

"""
this route allows users to login to the site
"""
@app.route("/login", methods=['GET', 'POST'])
def login():
    userForm = loginForm()
    if userForm.validate_on_submit():
        # check if an account with the username exists and if the password given matches the password stored
        user = Users.query.filter_by(username = userForm.username.data).first()
        if user and bcrypt.check_password_hash(user.userPass, userForm.user_pass.data):
            login_user(user, remember = userForm.rememberUser)
            page = request.args.get('next')
            flash(f'Welcome back {user.username}!', 'success')
            if page:
                return redirect(page)
            return redirect(url_for('home'))
        # user entered incorrect information, display error message 
        else:
            flash('Incorrect username or password. Please try again.', 'danger')
    return render_template('login.html', title='Login', form=userForm)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

"""
this route allows users to view all of their submitted pictures
"""
@app.route("/my-pictures")
@login_required
def user_pictures():
    userpic = "static/userpic.png"
    page = request.args.get("page", 1, type=int)
    images = Images.query.filter_by(owner = current_user).order_by(Images.datePosted.desc()).paginate(page=page, per_page=9)
    return render_template('imagedisp.html', images=images, title = 'My Pictures', profile_img = userpic, screen='user_pictures')

"""
this route allows users to upload images 
security: only jpeg/png/jpg files are accepted
          uploaded images are scanned to ensure 
          that they're truly photos
"""
@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == "POST":
        # go through the pictures the user uploaded and change the names
        # to a random hex string and save the image(s) to the proper directory
        # and save data to the database
        for file in request.files.getlist("file"):
            # user uploaded a file
            if file.filename != "":
                hex_val = secrets.token_hex(16)
                file_ext = str(file.filename).split(".")[1].lower()

                if file_ext == 'jpeg':
                    file_ext = 'jpg'

                # check to see if the images uploaded are valid pictures 
                if file_ext != validate_image(file.stream):
                    ext = validate_image(file.stream)
                    abort(406, "The image(s) uploaded were invalid.") 

                new_name = hex_val + '.' + file_ext

                # check if an image with that name already exists, if so; rename it
                while os.path.exists(new_name):
                    hex_val = secrets.token_hex(16)
                    new_name = hex_val + '.' + file_ext


                file.save(os.path.join(app.config['UPLOAD_PATH'], new_name)) 
                privimg = request.form.get('privimg')
                if privimg:
                    privflag = True
                   
                else:
                    privflag = False
                    
                newImage = Images(owner = current_user, imageName = new_name, privStatus = privflag)
                db.session.add(newImage)
                db.session.commit()


            else:
                flash("Please select an image to upload.", 'danger')
        if privflag:
            flash("Image(s) Uploaded!", 'success')
            flash("Your pictures will be kept private.", 'info')

        else:
            flash("Image(s) Uploaded!", 'success')
            flash("Your pictures will be displayed publicly.", 'info')
        return redirect(url_for('upload'))

    return render_template('upload.html', title = "Upload")

"""
this route allows users to view a particular image
"""
@app.route("/image/<int:imageID>", methods=['GET', 'POST'])
def image(imageID):
    image = Images.query.get_or_404(imageID)
    if image.owner != current_user:
        image = Images.query.filter(((Images.imageID == imageID) & (Images.privStatus == False))).first()
    if image == None:
        abort(403, "The image you tried to view is currently private. If you are the owner, please log in first.")

    img = PIL.Image.open(f"imagerepo/static/userimgs/{image.imageName}")
    width, height = img.size
    img_ext = img.format
    date = image.datePosted.strftime('%d/%m/%Y %H:%M')
    date = datetime.strptime(date, "%d/%m/%Y %H:%M")
    date = date.strftime('%d/%m/%Y %I:%M %p')

    if image.privStatus:
        status = "Off"
    else:
        status = "On"

    privimg = request.form.get('privimg')
    pubimg = request.form.get('pubimg')

    if privimg:
        image.privStatus = True
        db.session.commit()
        flash("Your image is now set to private view", 'success')
        return redirect(url_for('image', imageID=image.imageID))
        
    if pubimg:
        image.privStatus = False
        db.session.commit()
        flash("Your image is now set to public view", 'success')
        return redirect(url_for('image', imageID=image.imageID))
        

    return render_template('image.html', image=image, width=width, height=height, date=date, status=status, img_ext=img_ext)

"""
this route allows users to delete their selected image
"""
@app.route("/image/<int:imageID>/delete", methods=['POST'])
@login_required
def delete_image(imageID):
    image = Images.query.get_or_404(imageID)
    if image.owner != current_user:
        abort(403)

    else:
        filename = image.imageName
        os.remove(f"imagerepo/static/userimgs/{filename}")
        db.session.delete(image)
        db.session.commit()
        flash("Your image has been deleted!", "success")
        return redirect(url_for('home'))

@app.route("/deleteall", methods=['POST'])
@login_required
def delete_all():
    images = Images.query.filter_by(owner = current_user)
    
    # go through the user's images and delete them 
    for image in images:
        filename = image.imageName
        os.remove(f"imagerepo/static/userimgs/{filename}")
        db.session.delete(image)
        db.session.commit()
    flash("Your images have been deleted!", "success")
    return redirect(url_for('home'))

"""
this function validates whether or not a file is actually an image
credit: https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
"""
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return format if format != 'jpeg' else 'jpg'
