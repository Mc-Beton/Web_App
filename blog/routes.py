from flask import render_template, request, flash, url_for, redirect, session
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm
import functools

def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
      if session.get('logged_in'):
         return view_func(*args, **kwargs)
      return redirect(url_for('login', next=request.path))
   return check_permissions

def entrys(form, entry_id=None, entry=None):
   if form.validate_on_submit():
      if entry_id == None:
         entry = Entry(
            title=form.title.data,
            body=form.body.data,
            is_published=form.is_published.data
         )
         db.session.add(entry)
      else:
         form.populate_obj(entry)
      db.session.commit()
   else:
      errors = form.errors


@app.route("/")
def index():
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())

   return render_template("homepage.html", all_posts=all_posts)

@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
   form = EntryForm()
   errors = None
   if request.method == 'POST':
      entrys(form)
      return redirect(url_for('index'))

   return render_template("entry_form.html", form=form, errors=errors)

@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
   entry = Entry.query.filter_by(id=entry_id).first_or_404()
   form = EntryForm(obj=entry)
   errors = None
   if request.method == 'POST':
      entrys(form, entry_id=entry_id, entry=entry)
      return redirect(url_for('index'))

   return render_template("entry_form.html", form=form, errors=errors)

@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
      if form.validate_on_submit():
         session['logged_in'] = True
         session.permanent = True  # Use cookie to store session.
         flash('You are now logged in.', 'success')
         return redirect(next_url or url_for('index'))
      else:
         errors = form.errors
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'POST':
      session.clear()
      flash('You are now logged out.', 'success')
   return redirect(url_for('index'))

@app.route("/drafts/", methods=['GET'])
@login_required
def list_drafts():
   drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
   return render_template("drafts.html", drafts=drafts)
      
@app.route("/drafts/<int:entry_id>", methods=['POST'])
@login_required
def delete_entry(entry_id):
   if request.method == 'POST':
      if form.validate_on_submit():
         print(entry_id)
         entry = Entry.query.filter_by(id=entry_id).first_or_404()
         db.session.delete(entry)
         db.session.commit()
      else:
         errors = form.errors
      drafts2 = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
      return render_template("drafts.html", drafts2=drafts) 
