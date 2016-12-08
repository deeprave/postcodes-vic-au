# postcodes-vic-au
Google geocoded postcodes for Victoria, AU in JSON format.

I needed this data for a project that required an approximate location by postcode for the state of Victoria but didn't like the idea of having to use google geocode services for each request, and so obtained a freely available list of postcodes with location data.

Note that this list of postcodes includes only those that have a delivery area (and therefore have a location). PO Boxes and other special use postcodes are not included in the list.

After discovering that the data was inaccurate and in some cases just plain wrong, the script here was used to re-geocode the dataset using the google maps geocode service, and decided to post the result and make it available for others.

Note that google enforce daily and rate limits for geocoding queries, so the script allows for cycling a set of two or more api keys to get around this (two keys were used for this dataset). Be aware that running this on larger datasets will require a split into ~1000 or less items per batch (and there may be multiple items per postcode) using a single key, and running each batch run on separate 24 hour periods. Ultimately the _aim of this script is to **reduce**_ use of the geocoding service by generating and using locally cached data. For users with a google premium account, then the limit is 100k requests per day. See [here](https://developers.google.com/maps/documentation/geocoding/usage-limits) for more info.

The (python 3) script should be reusable for other similar use cases.  The only third party library used is [begins](https://pypi.python.org/pypi/begins), a very easy to use argparse front-end that has saved me a ton of time when writing scripts intended for command line use.

The script will require editing before use to insert your (one or more) google api keys.
