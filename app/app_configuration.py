from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required, current_user, utils, roles_required, user_registered, login_user
from app import app, db, user_datastore, security, dbconAg, dedicateddbconAg
from app.models.models import Specie, User
import os
import requests
import ldap

from config import obo,localNSpace,dcterms, SFTP_HOST
from franz.openrdf.vocabulary.rdf import RDF

# Executes before the first request is processed.
@app.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='end-user', description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = utils.encrypt_password(app.config['ADMIN_PASS'])
    if not user_datastore.get_user(app.config['ADMIN_EMAIL']):
        user_datastore.create_user(email=app.config['ADMIN_EMAIL'], password=encrypted_password, username=app.config['ADMIN_USERNAME'], name=app.config['ADMIN_NAME'])

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    specie1 = Specie(name="Campylobacter")
    specie2 = Specie(name="Yersinia")
    specie3 = Specie(name="E.coli")
    specie4 = Specie(name="Salmonella")

    if not db.session.query(Specie).filter(Specie.name == specie1.name).count() > 0:
        db.session.add(specie1)
    if not db.session.query(Specie).filter(Specie.name == specie2.name).count() > 0:
        db.session.add(specie2)
    if not db.session.query(Specie).filter(Specie.name == specie3.name).count() > 0:
        db.session.add(specie3)
    if not db.session.query(Specie).filter(Specie.name == specie4.name).count() > 0:
        db.session.add(specie4)

    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user(app.config['ADMIN_EMAIL'], 'admin')
    db.session.commit()

@app.login_manager.request_loader
def load_user_from_request(request):
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')

        try:
            result = User.try_login(username, password)
            print result
        except ldap.INVALID_CREDENTIALS, e:
            print e
            return None

        user = User.query.filter_by(username=result['uid'][0]).first()
        
        if not user:
            encrypted_password = utils.encrypt_password(password)
            if not user_datastore.get_user(result['mail'][0]):
                user = user_datastore.create_user(email=result['mail'][0], password=encrypted_password, username=result['uid'][0], name=result['cn'][0])
                db.session.commit()
        
        user = User.query.filter_by(username=result['uid'][0]).first()
        login_user(user)
        return user

@user_registered.connect_via(app) #overrides the handler function to add a default role to a registered user
def user_registered_handler(app, user, confirm_token):

    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], str(user.email) + '_' + str(user.id))):
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], str(user.email) + '_' + str(user.id)))
    
    default_role = user_datastore.find_role('end-user')
    user_datastore.add_role_to_user(user, default_role)
    db.session.commit()

    id= user.id

    ############# Add user to NGS_onto ########################

    UserURI = dbconAg.createURI(namespace=localNSpace, localname="users/"+str(id))
    userType = dbconAg.createURI(namespace=dcterms, localname="Agent")
    dbconAg.add(UserURI, RDF.TYPE, userType)

    '''
    ############## CREATE USER ON CONTROLLER ##############################
    r = requests.post('http://' + SFTP_HOST + '/controller/v1.0/users', data = {'username': user.email})
    print r.json()
    return 200
    '''
