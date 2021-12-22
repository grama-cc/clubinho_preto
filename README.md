# Clubinho Preto

Plataforma de administração do clubinho Preto, desenvolvido em Django

   
#### Install project dependencies:

    $ pip install -r requirements/local.txt
    
    
#### Then simply apply the migrations: 

    $ python manage.py migrate


#### Create an admin user: 

    $ python manage.py createsuperuser

    

#### Populate default instances: 

    $ python manage.py populate


#### You can now run the development server:

    $ python manage.py runserver