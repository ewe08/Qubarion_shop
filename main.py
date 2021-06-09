from flask import render_template, redirect, request
from flask import Flask
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os

from data import db_session
from data.products import Products
from data.users import User
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.products import ProductForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = r'static\img'
login_manager = LoginManager()
login_manager.init_app(app)
"""distances = [(['Огненный океан', "Сернистая пустыня"], 289),
             (['Глубокий каньон', "Сернистая пустыня"], 204),
             (['Огненный океан', "Глубокий каньон"], 170)]"""


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_sess = db_session.global_init(f"db/Qubarion.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/money', methods=['GET', 'POST'])
@login_required
def money():
    if request.method == 'GET':
        return render_template('money.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        try:
            db_sess.query(User).filter(User.id == current_user.id).update(
                {User.balance: User.balance + int(request.form['balance'])})
            db_sess.commit()
        except ValueError:
            return render_template('money.html',
                                   message="Я понимаю только цифры")
        return render_template('shop.html')


@app.route('/info')
@login_required
def info():
    db_sess = db_session.create_session()
    all_user_products = db_sess.query(Products).filter(Products.seller == current_user.id)
    return render_template("info.html", user=current_user, prods=all_user_products)


@app.route("/shop")
def shop():
    db_sess = db_session.create_session()
    prods = db_sess.query(Products).all()
    return render_template("shop.html", prods=prods)


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
            return redirect("/shop")
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
    try:
        form = ProductForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            assert str(form.price.data).isdigit()
            assert str(form.weight.data).isdigit()

            prod = Products(
                seller=current_user.id,
                product=form.product.data,
                price=form.price.data,
                weight=form.weight.data
            )
            current_user.products.append(prod)
            db_sess.merge(current_user)
            db_sess.commit()
            img = form.post_picture.data
            obj = str(db_sess.query(Products)[-1].id)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], f'{obj}.png'))
            return redirect('/shop')
        return render_template('products.html', title='Добавление Товара',
                               form=form)
    except Exception:
        return render_template('products.html', message="Данные введены неверно", form=form)


@app.route('/prod/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_prod(id):
    form = ProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id,
                                              Products.leader == current_user
                                              ).first()
        if prod:
            form.product.data = prod.product
            form.price.data = prod.price
            form.weight.data = prod.weight
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id,
                                              (Products.leader == current_user)
                                              ).first()
        if prod:
            prod.product = form.product.data
            prod.price = form.price.data
            prod.weight = form.weight.data
            db_sess.commit()
            return redirect('/shop')
        else:
            abort(404)
    return render_template('products.html',
                           title='Редактирование задания',
                           form=form
                           )


@app.route('/prod_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def prod_delete(id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Products).filter(Products.id == id,
                                          Products.leader == current_user).first()
    if prod:
        db_sess.delete(prod)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/shop')


@app.route('/prod_sell/<int:id>', methods=['GET', 'POST'])
@login_required
def sell_prod(id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Products).filter(Products.id == id).first()
    if current_user.balance >= prod.price and prod:
        prod.leader.already_sold += 1
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.balance -= prod.price
        os.remove(f'static/img/{prod.id}.png')
        db_sess.delete(prod)
        db_sess.commit()
    else:
        return render_template('shop.html',
                               message="Недостаточно денег")
    return redirect('/shop')


if __name__ == '__main__':
    main()
