#!/usr/bin/python
"""
Correct lat/lng of a postcodes file

Reads postcode data in JSON format and outputs either JSON or CSV
after checking the geocoding via google's geocoding API.

"""
from collections import OrderedDict
import begin
import json
import csv
from urllib.parse import urlencode
from urllib.request import urlopen


api_keys = [
	'insert_your_api_key_here',
	'insert_a_second_api_key_here'
]
country = 'AU'
state = 'VIC'


@begin.start
def main(tocsv: 'Output as CSV instead of JSON' =False,
        source: 'File to read' ='postcodes-vic.json',
        output: 'File to produce' ='postcodes-out.json'):
    """postcode converter"""
    src = []
    fieldnames = []
    try:
        if source.endswith('.csv'):
            with open(source, 'r', newline='') as csvsrc:
                reader = csv.DictReader(csvsrc)
                for row in reader:
                    if not fieldnames:  # preserve the field name in order
                        fieldnames = reader.fieldnames
                    if row[fieldnames[0]]:      # skip empty rows
                        rec = OrderedDict()
                        for field in fieldnames:
                            rec[field] = row[field]
                        src.append(rec)
            print('Read %d CSV record(s) from %s' % (len(src), source))
        else:
            with open(source, 'r') as fp:
                src = json.load(fp, object_pairs_hook=OrderedDict)
            print('Read %d JSON record(s) from %s' % (len(src), source))
            if len(src) > 0:        # may be needed for cvs output
                fieldnames = src[0].keys()

        if len(src) == 0:
            raise ValueError("ERROR: No data found?")

        failed = []
        fixcount = 0
        for row in src:
            # {"postcode":3000,"locality":"Melbourne","state":"VIC","lat":-37.81,"lng":144.97}
            if row['postcode'] <= 3999:
                query = {
                    'key': api_keys[fixcount % len(api_keys)],
                    'address': row['locality'],
                    'components': "country:%s|administrative_area_level_1:%s|postal_code:%u" % (country, state, row['postcode'])
                }
                url = None
                try:
                    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urlencode(query)
                    with urlopen(url) as req:
                        data = req.read()
                        jdata = json.loads(data.decode('utf-8'))    # should really be determined from headers
                        if jdata and 'status' in jdata:
                            if jdata['status'] == 'OK':
                                loc = jdata['results'][0]['geometry']['location']
                                if row['lat'] != loc['lat'] or row['lng'] != loc['lng']:
                                    print("Fixed %u: lat %.6f -> %.6f, lng %.6f -> %6f %s" % (row['postcode'], row['lat'], loc['lat'], row['lng'], loc['lng'], row['locality']))
                                    row['lat'] = loc['lat']
                                    row['lng'] = loc['lng']
                                    fixcount += 1
                            else:
                                print('Failed <%s> for postcode %u, %s' % (jdata['status'], row['postcode'], row['locality']))
                                row['failed'] = jdata['status']
                                if 'error_message' in jdata:
                                    row['message'] = jdata['error_message']
                                    failed.append(row)
                        else:
                            ValueError('request return no or invalid results for url %s' % (url, ))
                        pass
                except Exception as exc:
                    print("%s fetching %s" % (exc.__class__.__name__, url))
                    raise

        print("%u postcode errors fixed" % (fixcount,))

        with open(output, 'w', newline='') as out:
            if tocsv:
                csvwriter = csv.DictWriter(out, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
                csvwriter.writeheader()
                for row in src:
                    csvwriter.writerow(row)
            else:
                json.dump(src, out, separators=(',', ':'))

            print('Output %s: %d rows' % (output, len(src)))

        if failed:
            with open('failed-' + output, 'w', newline='') as out:
                json.dump(failed, out)

    except:
        raise

