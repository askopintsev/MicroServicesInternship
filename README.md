# AviDjango service documentation

This project was made during internship to work with popular frameworks and try to build microservice architecture.
Serivices are based on different approaches to get the best experience.
Services are built on REST logic, with dockerization.
Technologies applied:
- postgreSQL as shared database
- goods service:
   - django framework
   - django restframework
- user service:
   - aiohttp
   - sqlalchemy + alembic
   - redis as operational database
- monitoring service:
   - fastAPI
   - GinoORM + alembic
   - rabbitMQ for message queue
   - celery for worker consuming messages from queue
- mail service:
   - fastAPI
   - GinoORM + alembic
   - rabbitMQ for sending mails queue

### Mail_service API description
Mail_service API provides the following features:
<hr/>

* **Retrieve single mail template**

**URL:**  /mails/mail_id

Obligatory parameters:

- mail_id - id of mail template (integer)

<hr/>

* **Retrieve all mails templates**

**URL:**  /mails

Call of this endpoint will provides you full list of 
created mail templates.

<hr/>

* **Create mail template**

**URL:**  /mails/add

Obligatory parameters:

- text - text of mail template (string)

Creating mail template string you can use placeholders to
format text in future use. Available placeholders:
- {username},
- {password},
- {short_descr},
- {full_descr},
- {price},
- {created_at}

<hr/>

* **Delete mail template**

**URL:**  /mails/delete/mail_id

Obligatory parameters:

- mail_id - id of mail template (integer)

Call of this endpoint will provides you deletion of 
chosen mail template.

<hr/>

* **Send mail template**

**URL:**  /send/mail_id

Obligatory parameters:

- mail_id - id of mail template (integer)

Call of this endpoint will provides you sending of selected 
mail to addressee.

<hr/>

### Monitoring_service API description
Monitoring_service provides functionality for service's calls logging.
For correct call of service you need to use endpoint:

**URL:**  /events

System accepts the following parameters:
 - "request_timestamp" - datetime mark of request like: "2020-08-17 08:31:36",
 - "service" - service name string like: "User_service",
 - "url" - url of service request like,
 - "status_code" - code of service response (integer) like: 200,
 - "response_time" - datetime mark of request like: "2020-08-17 08:31:36"
<hr/>


### User_service API description
User_service API provides the following features:
<hr/>

* **Register in the service**

**URL:**  /register

Obligatory parameters:
- username
- password

You need to specify 'username' and 'password' parameters values 
to create your new user.
Your username must be unique, 
so you will receive system message if it's not.

After successfull request user will be created 
and you will be ready to login.

<hr/>

* **Login into the service**

**URL:**  /login

Obligatory parameters:
- username
- password

You need to pass authentification, so you need to enter
username and password of your created user. Otherwise, you
will receive error messages.
After successfull login you will be able to use the service.

Remember that session length is 15 minutes. 
After this period you can re-login 
or refresh your session with "/refresh" url.

<hr/>

* **Get and update profile info**

**URL:**  /profile

Non-obligatory parameters:
- new_username
- new_password

You need to be authorized to use this endpoint.

You can get your current profile info using this URL, such as:
user_id, username, password.

If you want to update your username or profile, 
you need to pass "new_username" and/or "new_password" 
via request.

<hr/>

* **Refresh your session**

**URL:**  /refresh

You need to be authorized to use this endpoint.

If your session is older than 15 minutes - 
it will expire. But you can refresh your session
using this URL without need to re-login.

Session refresh will work only for 
3 hours after your login action.
<hr/>

* **Logout from system**

**URL:**  /logout

You need to be authorized to use this endpoint.

You can end your session using this endpoint.
After that you need to login into system again 
to use system.

<hr/>

### Goods_service API description

Goods_service API provides the following features:
<hr/>

* **Get full list of existing tags in ads**:

Request will return list of tags used in ads

**URL:** /api/ad/tags/
<hr/>

* **Get short information from ad**

Request will return data from 'short_descr' field of ad

**URL:** /api/ad/id/short_info

id - required parameter - ID of the requested ad (digit)
<hr/>

* **Get full information from ad**

Request will return data from all ad's fields

**URL:** /api/ad/id

id - required parameter - ID of the requested ad (digit)
<hr/>

* **Update the fields of ad**

Request will update info in mentioned fields of given ad
and will update time in 'updated_at' field

**URL:** /api/id/?short_descr=value&full_descr=value&price=value

id - required parameter - ID of the requested ad (digit)

short_descr - optional parameter - new data for 
'short_descr' field (text)

full_descr - optional parameter - new data for 
'full_descr' field (text)

price - optional parameter - new data for 
'price' field (digits)
<hr/>

* **Filter ads by tags, price or date of publication**

Request will return ads with given search term

**URL:** api/ad/filter/?tags=value1,value2

**tags** - required parameter - search term, one tag name 
or several tags separated with comma

**min_date** - optional parameter, only ads created after 
this date will be returned,
if isn't specified, the value is used: '1900-01-01'.
Format: YYYY-MM-DD

**max_date** - optional parameter, only ads created before 
this date will be returned,
if isn't specified, the value is used: current date +1.
Format: YYYY-MM-DD

**min_price** - optional parameter, only ads with price 
bigger than this value will be returned,
if isn't specified, the value is used: 0.
(digit)

**max_price** - optional parameter, only ads with price
lower than this value will be returned,
if isn't specified, the value is used: 
maximum available price.
(digit)
<hr>

* **Work with ad image**

Request allows to work with image of ad: add image, 
update image, delete image

**URL:** api/ad/id/image/?photo=value

id - required parameter - ID of the requested ad (digit)

photo - required parameter
* in case of add or update image - you need to provide 
 url to selected image for id (url)
* in case of delete image - you need to pass as value 
string 'delete'
