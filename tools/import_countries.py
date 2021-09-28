import csv

from profiles.models import Country
from django.db import IntegrityError

with open('../fixtures/countries_list.tsv', newline='', encoding="utf8") as csvfile:
    country_reader = list(csv.reader(csvfile, delimiter='\t', quotechar='|'))[1:]
    for row in country_reader:
        c = Country(
            code=row[0],
            name=row[1],
            is_under_represented=(row[2]=='1')
        )
        c.save()  