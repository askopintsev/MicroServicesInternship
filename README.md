# AviDjango service documentation

### API description

AviDjango API provides the following features:
<hr/>

* **Get full list of existing tags in ads**:

Request will return list of tags used in ads

**URL:** /api/tags/
<hr/>

* **Get short information from ad**

Request will return data from 'short_descr' field of ad

**URL:** /api/short/id

id - required parameter - ID of the requested ad (digit)
<hr/>

* **Get full information from ad**

Request will return data from all ad's fields

**URL:** /api/full/id

id - required parameter - ID of the requested ad (digit)
<hr/>

* **Update the fields of ad**

Request will update info in mentioned fields of given ad
and will update time in 'updated_at' field

**URL:** /api/update/id/?short_descr=value&full_descr=value&price=value

id - required parameter - ID of the requested ad (digit)

short_descr - optional parameter - new data for 
'short_descr' field (text)

full_descr - optional parameter - new data for 
'full_descr' field (text)

price - optional parameter - new data for 
'price' field (digits)
<hr/>

* **Select ads by tags**

Request will return ads with given tags

**URL:** api/tagsfilter/?tags=value1,value2

tags - required parameter - search term, one tag name 
or several tags separated with comma
<hr/>

* **Filter ads by dates**

Request will return ads created between given dates

**URL:** api/datesfilter/?min_date=value&max_date=value

min_date - optional parameter, only ads created after 
this date will be returned,
if isn't specified, the value is used: '1900-01-01'.
Format: YYYY-MM-DD

max_date - optional parameter, only ads created before 
this date will be returned,
if isn't specified, the value is used: current date +1.
Format: YYYY-MM-DD
<hr>

* **Filter ads by price**

Request will return ads with price between given values

**URl:** api/pricefilter/?min_price=value&max_price=value

min_price - optional parameter, only ads with price 
bigger than this value will be returned,
if isn't specified, the value is used: 0.
(digit)

max_price - optional parameter, only ads with price
lower than this value will be returned,
if isn't specified, the value is used: 
maximum available price.
(digit)
<hr>

* **Work with ad image**

Request allows to work with image of ad: add image, 
update image, delete image

**URL:** api/image/id/?command=value&image_url=value

id - required parameter - ID of the requested ad (digit)

command - required parameter - type of action with image
in add. Allowed values: _add_, _update_, _delete_.
If value is _add_ or _update_ than 'image_url' parameter
 is required
 
image_url - required parameter in case of command=add
 or update - url to selected image for id (url)
