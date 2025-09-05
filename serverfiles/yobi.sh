#!/bin/sh

expline = " AND line != 'オートフライヤー'"

sudo -u postgres psql -U postgres postgres -c "UPDATE kouteikanri_chouriproc SET startj = starty WHERE hinban < 1000 AND startj IS NULL AND starty <= CURRENT_TIMESTAMP" + expline + ";"
sudo -u postgres psql -U postgres postgres -c "UPDATE kouteikanri_chouriproc SET endj = endy, status = 1 WHERE hinban < 1000 AND endj IS NULL AND endy <= CURRENT_TIMESTAMP" + expline + ";"
