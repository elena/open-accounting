# Open Accounting
with Subledgers

Version: 0.0.1a <br>
Current Django version: 2.0.9  <br>
Author: Elena Williams

For quick-start accounting for people who have been forced to do a lot of it,
and are accustomed to getting the crappy end.

Intended as an app that reduces busy-work and duplication.

Primary goals are to:
 - #1 Remove "Pain Points" from the Accounting and Bookkeeping process
 - #2 Speed (loading speed, report viewing speed, see #1)
 - #3 Efficiency

Respect goes to previous respectable open source accounting and bookkeeping
projects, which were explored:

- https://www.gnucash.org/
- http://furius.ca/beancount/
- https://github.com/dulaccc/django-accounting
- https://github.com/prikhi/AcornAccounting
- https://github.com/SwingTix/bookkeeper

Please let me know if there are other FOSS accounting projects to add to this list.

The most notable difference to the mature FOSS projects are "sub-ledgers", such as
accounts payable and bank reconciliations. These are deal-breakingly important
and larger to implement than the "general ledger" (ie straight double-entry).

Moreover the biggest priority of this project surrounds ease of data input about
which the author has strong views. The implementation of this feature seemed too
large and difficult to back-port in to an existing project, though the prospect
was explored.

Full project write up here:
http://open-accounting.blogspot.com.au/



========== <br>
Fri Jun 30 14:39:31 AEST 2017  <br>
v 0.0.1a


This first version is ** VERY OPINIONATED **.

Biggest bits of opinionation is use of GST as required for Australian SAAP and
Australian forms of bank accounts and Australian Financial Years dates.

This version allows

 - General Ledgers
 - Basic Contacts (as entities)

 - Subledgers:
   - Accounts Payable
   - Expenses
   - Sales
   - Manual Journal Entries
   - Bank Statements/reconciliations


The biggest feature is bulk uploads from spreadsheet for:
- bank statements
- any subledger types

Reporting is woeful in this version.

Number of tests: 125
