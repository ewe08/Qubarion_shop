from flask import render_template, redirect, request
from flask import Flask
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.exceptions import abort

from data import db_session
from data.products import Products
from data.users import User
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.products import ProductForm

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
    app.run(port=5000, host='127.0.0.1')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    prods = db_sess.query(Products).all()
    return render_template("index.html", prods=prods)


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


@app.route('/addprod', methods=['GET', 'POST'])
@login_required
def add_prod():
    form = ProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        prod = Products(
            seller=current_user.id,
            product=form.product.data,
            price=form.price.data,
            weight=form.weight.data
        )
        current_user.products.append(prod)
        db_sess.merge(current_user)
        db_sess.commit()
        f = form.post_picture.data
        save_image(f, prod.id)
        return redirect('/')
    return render_template('jobs.html', title='Добавление Товара',
                           form=form)


def save_image(data, name):
    with open(f'static/img/{name}.jpg', 'wb') as handler:
        handler.write(data)


"""@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
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
        jobs = db_sess.query(Product).filter(Product.id == id,
                                          ((Product.leader == current_user) | (current_user.id == 1))
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
    jobs = db_sess.query(Product).filter(Product.id == id,
                                      ((Product.leader == current_user) | (current_user.id == 1))
                                      ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')

"""
if __name__ == '__main__':
    main()
