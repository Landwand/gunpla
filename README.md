# GUNPLA 
(in progress)


## DESCRIPTION:
Portmanteau of __Gundam-Plastic-Model__. This is a browser-based inventory app for tracking my problem of buying to many plastic models.  Currently uses Flask is its backbone. The end-goal is to have a REST-API back-end along with a React UI.

A new user will be able to:

1. visit homepage
2. optionally create an account / login
3. **view**, **add** or **edit** their collection of plastic models
4. display their shame for wasting so much money


**HOMEPAGE**

<img width="698" alt="image" src="https://github.com/Landwand/gunpla/assets/56357681/a8d6f1fb-97e5-4388-b2dd-630b9f1ff89f">

**Inventory View**

<img width="707" alt="image" src="https://github.com/Landwand/gunpla/assets/56357681/8d8e45ef-dc42-48b6-a596-d65ef7d19ed3">


## Installation and running instructions

1. clone the repo
2. `cd` into the respective folder
3. create a Python virtual environment using [venv](https://docs.python.org/3/library/venv.html) using the command `python -m venv your-virtual-env-name`
5. start the virtual environment using `source your-virtual-env-name/bin/activate`
6. install dependencies using [pip freeze](https://pip.pypa.io/en/stable/cli/pip_freeze/) using the command, `pip install -r requirements.txt`
7. run using the command `flask run` -or- use debug mode to see app messaging and enjoy instant-reloading of changes by using `flask run --debug`

## Login

Feel free to create your own account and play around with it, or use this 'highly secure' existing login:

- Username : **w**
- Password: **w**

## API
=======

### API-Login

`http://localhost:5000/api/login`

Supported HTTP methods: GET, POST

Example: using GET to check whether you're logged-in

```
GET /api/login HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: ******
```

Response:

```

{
    "message": "You are logged in!"
}

```

Example: using POST to login:

```
POST /api/login HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: ********
Content-Length: 42

{
   "username": "w",
   "password": "w"
}
```

Response:

```
{
    "message": "API login successful."
}
```


###API-Logout

`http://localhost:5000/api/logout`

Supported HTTP methods: POST

Example:

```
POST /api/logout HTTP/1.1
Host: localhost:5000
Content-Type: application/json

```

Response:

```
[
    {
        "message": "Successfully logged out."
    },
    200
]
```

###API-Kits
`http://localhost:5000/api/kits`

Supported HTTP methods: GET

Example:
```
GET /api/kits HTTP/1.1
Host: localhost:5000
Cookie: ******
```

Response:
```
{
    "kits": [
        {
            "condition": "snapped",
            "grade": "hg",
            "id": 1,
            "material": "plastic",
            "name": "Sheng Long",
            "notes": "HGAC2",
            "owner_id": 1,
            "scale": 144
        },
        {
            "condition": "progress",
            "grade": "hg",
            "id": 2,
            "material": "plastic",
            "name": "Heavyarms",
            "notes": "HGAC opened.",
            "owner_id": 1,
            "scale": 144
        },
        // ... (truncated for brevity)
        {
            "condition": "new",
            "grade": "None",
            "id": 23,
            "material": "plastic",
            "name": "SSS 2002 ver Knight of Gold w Buster Launcher",
            "notes": "recast",
            "owner_id": 1,
            "scale": 100
        }
    ]
}
'''


