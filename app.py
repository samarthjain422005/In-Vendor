from flask import Flask, render_template,request,redirect,url_for,flash
from flask import SQLALchemy
from flask_login import UserMixin,login_user,login_required,logout_user,current_user, LoginManager
from SQLALchemy import func
from datetime import date
from SQLALchemy import create_engine

#database
db=SQLALchemy()
DB_NAME="database.db"

class Billing(db.Model):
  username=db.Column(db.String(150),ForeignKey='user.username')
  id=db.Column(db.Integer,unique=True)


class User(db.Model,UserMixin):
  id=db.Column(db.Integer,unique=True)
  username=db.Column(db.String(150),primary_key=True)
  store_name=db.Column(db.String(150),unique=True)
  email=db.Column(db.String(150),unique=True)
  password=db.Column(db.String(150),unique=True)
  city=db.Column(db.String(150))
  country=db.Column(db.String(150))
  store_category=db.Column(db.String(150))
  billing=db.relationship('Billing')


db.create_all()

 
#page routing
@app.route("/")
def landing_page():
  return render_template('landing page.html')

@app.route("/logout")
@login_required
def logout():
  logout_user() 
  return redirect(url_for("landing_page"))

@app.route("/home")
@login_required
def home():
  return render_template('home.html',user=current_user)
  


@app.route("/sign-up",methods=['GET','POST'])
def sign_up():
  if request.method=='POST':
    username=request.form.get('username')
    store_name=request.form.get('organisation name')
    email=request.form.get('email')
    password1=request.form.get('password')
    password2=request.form.get('confirm password')
    city=request.form.get('city')
    country=request.form.get('country')
    store_category=request.form.get('store category')

    user=User.query.filter_by(username=username).first()
    if user:
      flash("Username already exists",category='error')
    elif len(email)<4:
      flash("Email must be greater than 4 characters",category='error')
    elif len(username)<2:
      flash("Username must be greater than 2 characters",category='error')
    elif password1!=password2:
      flash("Passwords don't match",category='error')
    elif len(password1)<7:
      flash("Password less than 7",category='error')
    else:
      new_user=User(username=username,store_name= store_name,email=email,password=password1,city=city,country=country,store_category=store_category)
      db.session.add(new_user)
      db.session.commit()
      login_user(user,remember=True)
      flash("Account created!!",category='success')
      return redirect(url_for('home'))
      
    
  return render_template('sign-up.html',user=current_user)


@app.route("/login",methods=['GET','POST'])
def login():
  if request.method=="POST":
    username=request.form.get('username')
    password=request.form.get('password')

    user=User.query.filter_by(username=username).first()
    if user:
      if user.password==password:
        flash("Logged in Successfully!!",category="success")
        login_user(user,remember=True)
        return redirect(url_for('home'))
      else:
        flash("Incorrect password , try again",category="error")
    else:
      flash("Username doesn't exist",category="error")
  return render_template('login.html',user=current_user)

@app.route("/billing")
@login_required
def billing():
  return render_template('billing.html',user=current_user)

@app.route("/billing/new-bill")
@login_required
def new_bill():
  if request.method=="POST":
    bill_no_temp=db.session.query(func.max(id)).all()
    bill_no_temp1=int(bill_no_temp[12:])
    username=current_user
    store_id=User.query.filter_by(username=username).first()
    date=date.today()
    bill_no=date+"-"+store_id+"-"+str(bill_no_temp1+1)
    name=request.form.get('customer_name')
    mobile_no=request.form.get('mobile_no')
    no_of_item=request.form.get('no_of_item')
    maxitem=99
    if (no_of_item>maxitem):
        print()
        flash("Please enter less than 99 items or split the bill into two",category="error")
    elif (no_of_item<=maxitem) :
        for a in range(no_of_item):
          if i<10:
            s_no=bill_no+'xx0'+str(a)
            product_code=request.form.get('no_of_item')
            rec=Products.query.filter_by(username=username).first()
            for r in rec:
                product_name=r[2]
                mrp=r[3]
                sgst=r[4]
                cyst=r[5]
                qty=r[6]
                stock_available=r[7]
            quantity=request.form.get('quantity')
            t=(mrp+sgst+cgst)*quantity
            j=Billing(store_id=store_id,bill_no=bill_no, s_no=s_no, date=date, name=date, mobile_no=mobile_no, product_name=product_name, product_code=product_code, mrp=mrp, quantity=quantity, sgst=sgst, cgst=cgst, total=t)
            db.session.add(j)
            db.session.commit()
            upd = update(Products)
            val = upd.values({"stock":"stock_available-quantity"})
            cond = val.where(Products.c.product_id == product_code)
            engine.execute(upd)
            
            w=qty+quantity
            upd = update(Products)
            val = upd.values({"quatity_sold":"w"})
            cond = val.where(Products.c.product_id == product_code)
            engine.execute(upd)
            
            record=Taxes.query.filter_by(product_id=product_code).first()
            for u in record:
              quantity_sold=u[2]+quantity
              gst_collected=u[3]+(sgst+cgst)*quantity
            upd = update(Taxes)
            val = upd.values({"quantity_sold":"quantity_sold"},{"gst_collected":"gst_collected"},{"status":"Due"})
            cond = val.where(Billing.c.product_id == product_code)
            engine.execute(upd)
                              
          else:
            s_no=bill_no+'xx'+str(a)
            product_code=request.form.get('no_of_item')
            rec=Products.query.filter_by(username=username).first()
            for r in rec:
                product_name=r[2]
                mrp=r[3]
                sgst=r[4]
                cyst=r[5]
                qty=r[6]
                stock_available=r[7]
            quantity=request.form.get('quantity')
            t=(mrp+sgst+cgst)*quantity
            j=Billing(store_id=store_id,bill_no=bill_no, s_no=s_no, date=date, name=date, mobile_no=mobile_no, product_name=product_name, product_code=product_code, mrp=mrp, quantity=quantity, sgst=sgst, cgst=cgst, total=t)
            db.session.add(j)
            db.session.commit()
            upd = update(Products)
            val = upd.values({"stock":"stock_available-quantity"})
            cond = val.where(Products.c.product_id == product_code)
            engine.execute(upd)
            
            w=qty+quantity
            upd = update(Products)
            val = upd.values({"quatity_sold":"w"})
            cond = val.where(Products.c.product_id == product_code)
            engine.execute(upd)
            
            record=Taxes.query.filter_by(product_id=product_code).first()
            for u in record:
              quantity_sold=u[2]+quantity
              gst_collected=u[3]+(sgst+cgst)*quantity
            upd = update(Taxes)
            val = upd.values({"quantity_sold":"quantity_sold"},{"gst_collected":"gst_collected"},{"status":"Due"})
            cond = val.where(Billing.c.product_id == product_code)
            engine.execute(upd)
              
    flash("Billing Success!!",category="success")
    
    
  return render_template('new bill.html',user=current_user)




#main
def create_app():
  app=Flask(__name__)
  db.app(app)
  login_manager=LoginManager()
  login_manager.login_view='login'
  login_manager.app(app)

  @login_manager.user_loader
  def load_user(id):
    return User.query.get(username)

  


app.run(host='0.0.0.0',debug=True)