from flask import render_template, redirect, request
from flask import Flask
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.exceptions import abort

from data import db_session
from data.products import Product
from data.users import User
#from data.departments import Department
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.jobs import JobsForm
from forms.departments import DepartmentsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_sess = db_session.global_init(f"db/mars_explorer.db")
    app.run(port=8000, host='127.0.0.1')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Product).all()
    return render_template("index.html", jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            place=form.place.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        prod = Product()
        prod.job = form.job.data
        prod.team_leader = form.team_leader.data
        prod.work_size = form.work_size.data
        prod.collaborators = form.collaborators.data
        prod.is_finished = form.is_finished.data
        current_user.jobs.append(prod)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление новости',
                           form=form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        prod = db_sess.query(Product).filter(Product.id == id,
                                             ((Product.leader == current_user) | (current_user.id == 1))
                                             ).first()
        if prod:
            form.job.data = prod.job
            form.team_leader.data = prod.team_leader
            form.work_size.data = prod.work_size
            form.collaborators.data = prod.collaborators
            form.is_finished.data = prod.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          ((Jobs.leader == current_user) | (current_user.id == 1))
                                          ).first()
        if jobs:
            jobs.job = form.job.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html',
                           title='Редактирование задания',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                      ((Jobs.leader == current_user) | (current_user.id == 1))
                                      ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/departments")
def departments():
    db_sess = db_session.create_session()
    deps = db_sess.query(Department)
    return render_template("department.html", deps=deps)


@app.route('/adddep', methods=['GET', 'POST'])
@login_required
def add_dep():
    form = DepartmentsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = Department()
        dep.title = form.title.data
        dep.chief = form.chief.data
        dep.members = form.members.data
        dep.email = form.email.data
        current_user.deps.append(dep)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/departments')
    return render_template('add_dep.html', title='Добавление',
                           form=form)


@app.route('/dep_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def dep_delete(id):
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).filter(Department.id == id,
                                           ((Department.user == current_user) | (
                                                   current_user.id == 1))
                                           ).first()
    if dep:
        db_sess.delete(dep)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route('/dep/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dep(id):
    form = DepartmentsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        dep = db_sess.query(Department).filter(Department.id == id,
                                               ((Department.user == current_user) | (
                                                       current_user.id == 1))
                                               ).first()
        if dep:
            form.title.data = dep.title
            form.chief.data = dep.chief
            form.members.data = dep.members
            form.email.data = dep.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = db_sess.query(Department).filter(Department.id == id,
                                               ((Department.user == current_user) | (
                                                       current_user.id == 1))
                                               ).first()
        if dep:
            dep.title = form.title.data
            dep.chief = form.chief.data
            dep.members = form.members.data
            dep.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('add_dep.html',
                           title='Редактирование',
                           form=form
                           )


if __name__ == '__main__':
    main()
