# Open Accounting
with Subledgers

Version: 0.0.1a
Current Django version: 1.11.2
Author: Elena Williams

For quick-start accounting for people who have been forced to do a lot of it,
and are accustomed to getting the crappy end.

Intended as an app that reduces busy-work and duplication.

Primary goals are to:
 - #1 Remove "Pain Points" from the Accounting and Bookkeeping process
 - #2 Speed (loading speed, report viewing speed, see #1)
 - #3 Efficiency


==========
Fri Jun 30 14:39:31 AEST 2017
v 0.0.1a


Full write up here: http://open-accounting.blogspot.com.au/

This first version is ** VERY OPINIONATED **.

Biggest bits of opinionation is use of GST as required for Australian SAAP and
Australian forms of bank accounts.

This version allows

 - General Ledgers
 - Basic Contacts (as entities)

 - Subledgers:
   - Accounts Payable
   - Expenses
   - Bank Statements/reconciliations

The biggest feature is bulk uploads from spreadsheet for:
- bank statements
- subledgers

Number of tests: 125
